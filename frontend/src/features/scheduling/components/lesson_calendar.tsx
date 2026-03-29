'use client'

import React, { useEffect, useState, useMemo, useRef } from 'react'
import { faPencil, faTrash, faCheck, faXmark, faChevronLeft, faChevronRight, faPlus } from '@fortawesome/free-solid-svg-icons'
import { Lesson } from '../../../types/index'
import { getLessons, deleteLesson } from '../api/lesson'
import Button from '@/components/ui/button'
import ScheduleLessonModal from './schedule_lesson_modal'

type CalendarView = 'month' | 'week' | 'day'

const WEEK_DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const MONTH_DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

function parseISODateToLocal(dstr: string) {
  if (!dstr) return new Date(dstr)
  try {
    if (/^\d{4}-\d{2}-\d{2}$/.test(dstr)) {
      const parts = dstr.split('-').map(p => Number(p))
      return new Date(parts[0], parts[1] - 1, parts[2])
    }
    const m = dstr.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})/)
    if (m) {
      const y = Number(m[1]), mo = Number(m[2]), da = Number(m[3])
      const hh = Number(m[4]), mm = Number(m[5]), ss = Number(m[6])
      return new Date(y, mo - 1, da, hh, mm, ss)
    }
  } catch (e) { /* fallback */ }
  return new Date(dstr)
}

function startOfWeek(d: Date) {
  const date = new Date(d)
  const day = date.getDay()
  const diff = (day === 0 ? -6 : 1) - day
  date.setDate(date.getDate() + diff)
  date.setHours(0, 0, 0, 0)
  return date
}

function startOfDay(d: Date) {
  const date = new Date(d)
  date.setHours(0, 0, 0, 0)
  return date
}

function startOfMonth(d: Date) {
  return new Date(d.getFullYear(), d.getMonth(), 1)
}

function sameDay(a: Date, b: Date) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
}

function formatDateLocal(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

function getStatusColor(status: string | null | undefined): string {
  const colors: Record<string, string> = {
    'Scheduled': '#C3E4FF',
    'Completed': '#C3FFD7',
    'Cancelled': '#FFED7A',
  }
  return colors[status ?? ''] || '#cfe9ff'
}

function getTextColor(bg: string): string {
  const textForBg: Record<string, string> = {
    '#C3E4FF': '#0B3A66',
    '#C3FFD7': '#0B6B3B',
    '#FFED7A': '#7A5D00',
  }
  return textForBg[bg] || '#000'
}

interface LessonCalendarProps {
  onWeekChange?: (d: Date) => void
  onLessonCreated?: () => void
}

const LessonCalendar: React.FC<LessonCalendarProps> = ({ onWeekChange, onLessonCreated }) => {
  const [view, setView] = useState<CalendarView>('week')
  const [cursor, setCursor] = useState<Date>(startOfWeek(new Date()))
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [showModal, setShowModal] = useState(false)
  const [calendarEditMode, setCalendarEditMode] = useState(false)
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null)
  const panelRef = useRef<HTMLDivElement | null>(null)
  const [rowHeightPx, setRowHeightPx] = useState<number>(54)
  const [rowGapPx, setRowGapPx] = useState<number>(0)

  async function fetchLessons() {
    let start: string, end: string
    if (view === 'month') {
      const first = startOfMonth(cursor)
      const last = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0)
      start = formatDateLocal(first)
      end = formatDateLocal(last)
    } else if (view === 'week') {
      start = formatDateLocal(cursor)
      end = formatDateLocal(new Date(cursor.getTime() + 6 * 24 * 60 * 60 * 1000))
    } else {
      start = formatDateLocal(cursor)
      end = formatDateLocal(cursor)
    }

    try {
      const data = await getLessons(start, end)
      console.debug('[LessonCalendar] fetched lessons count=', Array.isArray(data) ? data.length : 0)
      setLessons(data)
    } catch (error) {
      console.error('[LessonCalendar] Error fetching lessons:', error)
    }
  }

  useEffect(() => { fetchLessons() }, [cursor, view])

  useEffect(() => {
    if (onWeekChange) onWeekChange(cursor)
  }, [cursor, onWeekChange])

  useEffect(() => {
    function measure() {
      try {
        const el = panelRef.current
        if (!el) return
        const cs = getComputedStyle(el)
        const rh = parseFloat(cs.getPropertyValue('--row-height')) || 54
        const rg = parseFloat(cs.getPropertyValue('--row-gap')) || 0
        setRowHeightPx(rh)
        setRowGapPx(rg)
      } catch (e) { /* ignore */ }
    }
    measure()
    window.addEventListener('resize', measure)
    return () => window.removeEventListener('resize', measure)
  }, [])

  const viewDays = useMemo(() => {
    if (view === 'week') {
      return Array.from({ length: 5 }).map((_, i) => {
        const d = new Date(cursor)
        d.setDate(d.getDate() + i)
        return d
      })
    } else if (view === 'day') {
      return [new Date(cursor)]
    }
    return []
  }, [view, cursor])

  const layoutMap = useMemo(() => {
    if (view === 'month') return {}
    const map: Record<string, { col: number, total: number }> = {}
    const dayLessons: Lesson[][] = viewDays.map(() => [])

    for (const lesson of lessons) {
      const ld = parseISODateToLocal(lesson.start_time)
      for (let i = 0; i < viewDays.length; i++) {
        if (sameDay(ld, viewDays[i])) {
          dayLessons[i].push(lesson)
          break
        }
      }
    }

    for (let dayIdx = 0; dayIdx < viewDays.length; dayIdx++) {
      const evs = dayLessons[dayIdx].map(lesson => {
        const start = lesson.start_time ? new Date(lesson.start_time) : null
        const end = lesson.end_time ? new Date(lesson.end_time) : null
        const defaultStart = 9
        const sHour = start ? start.getHours() : defaultStart
        const sMin = start ? start.getMinutes() : 0
        const eHour = end ? end.getHours() : (sHour + 1)
        const eMin = end ? end.getMinutes() : 0
        const startTotal = sHour + sMin / 60
        const endTotal = eHour + eMin / 60
        return { lesson, startTotal, endTotal }
      }).sort((a, b) => a.startTotal - b.startTotal)

      const columnsEnd: number[] = []
      for (const item of evs) {
        let placed = false
        for (let ci = 0; ci < columnsEnd.length; ci++) {
          if (columnsEnd[ci] <= item.startTotal) {
            map[item.lesson.lesson_id] = { col: ci, total: 0 }
            columnsEnd[ci] = item.endTotal
            placed = true
            break
          }
        }
        if (!placed) {
          columnsEnd.push(item.endTotal)
          map[item.lesson.lesson_id] = { col: columnsEnd.length - 1, total: 0 }
        }
      }
      const totalCols = columnsEnd.length || 1
      for (const item of evs) {
        if (map[item.lesson.lesson_id]) map[item.lesson.lesson_id].total = totalCols
      }
    }

    return map
  }, [lessons, viewDays, view])

  function prev() {
    if (view === 'month') {
      setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))
    } else if (view === 'week') {
      setCursor(new Date(cursor.getTime() - 7 * 24 * 60 * 60 * 1000))
    } else {
      setCursor(new Date(cursor.getTime() - 24 * 60 * 60 * 1000))
    }
  }

  function next() {
    if (view === 'month') {
      setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))
    } else if (view === 'week') {
      setCursor(new Date(cursor.getTime() + 7 * 24 * 60 * 60 * 1000))
    } else {
      setCursor(new Date(cursor.getTime() + 24 * 60 * 60 * 1000))
    }
  }

  function goToday() {
    if (view === 'month') {
      setCursor(startOfMonth(new Date()))
    } else if (view === 'week') {
      setCursor(startOfWeek(new Date()))
    } else {
      setCursor(startOfDay(new Date()))
    }
  }

  function switchView(v: CalendarView) {
    if (v === 'month') setCursor(startOfMonth(cursor))
    else if (v === 'week') setCursor(startOfWeek(cursor))
    else setCursor(startOfDay(cursor))
    setView(v)
  }

  const hours = Array.from({ length: 11 }).map((_, i) => 8 + i)

  async function handleDeleteLesson(lessonId: string) {
    if (!confirm('Delete this lesson?')) return
    try {
      await deleteLesson(lessonId)
      await fetchLessons()
      if (onLessonCreated) onLessonCreated()
    } catch (error) {
      console.error('[LessonCalendar] Delete error:', error)
      alert('Failed to delete lesson')
    }
  }

  function renderLessonBlock(lesson: Lesson, dayIdx: number) {
    const start = lesson.start_time ? new Date(lesson.start_time) : null
    const end = lesson.end_time ? new Date(lesson.end_time) : null
    const defaultStart = 9
    const sHour = start ? start.getHours() : defaultStart
    const sMin = start ? start.getMinutes() : 0
    const eHour = end ? end.getHours() : (sHour + 1)
    const eMin = end ? end.getMinutes() : 0

    const startTotalHours = (sHour + sMin / 60)
    const endTotalHours = (eHour + eMin / 60)
    const visibleStart = 8
    const visibleEnd = 18

    if (endTotalHours <= visibleStart || startTotalHours >= visibleEnd) return null

    const clampedStart = Math.max(startTotalHours, visibleStart)
    const clampedEnd = Math.min(endTotalHours, visibleEnd)
    const durationHours = Math.max(0.25, clampedEnd - clampedStart)

    const totalSlotHeight = rowHeightPx + rowGapPx
    const top = (clampedStart - visibleStart) * totalSlotHeight
    const height = durationHours * totalSlotHeight - rowGapPx

    const bg = getStatusColor(lesson.status)
    const textColor = getTextColor(bg)

    const layout = layoutMap[lesson.lesson_id] || null
    const style: React.CSSProperties = {
      top: `${top}px`,
      height: `${height}px`,
      position: 'absolute',
      background: bg,
      borderRadius: 10,
      color: textColor,
      paddingTop: 8,
      paddingLeft: 10,
      zIndex: 10,
      cursor: 'pointer'
    }

    if (layout) {
      const col = layout.col
      const total = layout.total || 1
      const widthPct = 100 / total
      const leftPct = col * widthPct
      style.left = `${leftPct}%`
      style.width = `calc(${widthPct}% - 8px)`
      style.zIndex = 20 + col
    } else {
      style.left = '4px'
      style.right = '4px'
    }

    const timeLabel = start
      ? `${start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}${end ? ' - ' + end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''}`
      : ''

    return (
      <div
        key={lesson.lesson_id}
        className={`ac-event ac-event-${dayIdx}`}
        style={style}
        title={`${lesson.status ?? 'Lesson'} — ${timeLabel}`}
      >
        {calendarEditMode && (
          <div className="event-btns-wrapper" style={{ position: 'absolute', top: 6, right: 6, zIndex: 60 }} onClick={(e) => e.stopPropagation()}>
            <Button variant="event-edit"   icon={faPencil} onClick={() => { setEditingLesson(lesson); setShowModal(true) }} title="Edit lesson" />
            <Button variant="event-delete" icon={faTrash}  onClick={() => handleDeleteLesson(lesson.lesson_id)} title="Delete lesson" />
          </div>
        )}
        <div className="ac-event-name" style={{ fontWeight: 'bold' }}>
          {lesson.status ?? 'Lesson'}
        </div>
        <div className="ac-event-time" style={{ fontSize: '0.8rem', marginTop: 4 }}>
          {timeLabel}
        </div>
      </div>
    )
  }

  function renderTimeGrid(days: Date[], dayLabels: string[]) {
    const colCount = days.length
    return (
      <>
        <div className="week-nav">
          <div className="nav-group">
            <Button variant="icon" icon={faChevronLeft}  onClick={prev} title="Previous" />
            <Button variant="icon" icon={faChevronRight} onClick={next} title="Next" />
          </div>
          <div className="days-row" style={{ gridTemplateColumns: `repeat(${colCount}, 1fr)` }}>
            {days.map((d, idx) => (
              <div key={idx} className="day-header">
                <div className="day-name">{dayLabels[idx]}</div>
                <div className="day-date">{d.getDate()}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="calendar-grid">
          <div className="time-col">
            {hours.map(h => (
              <div key={h} className="time-cell">
                <div className="hour-inner">
                  {h < 12 ? `${h} AM` : (h === 12 ? '12 PM' : `${h - 12} PM`)}
                </div>
              </div>
            ))}
          </div>
          <div className="days-col" style={{ gridTemplateColumns: `repeat(${colCount}, 1fr)` }}>
            {days.map((d, dayIdx) => (
              <div key={dayIdx} className="day-column">
                <div className="day-grid" style={{ gridTemplateRows: `repeat(${hours.length}, 1fr)` }}>
                  {hours.map(h => (
                    <div key={h} className="slot-cell" data-hour={h}></div>
                  ))}
                  {lessons.filter(lesson => {
                    const ld = parseISODateToLocal(lesson.start_time)
                    return sameDay(ld, d)
                  }).map(lesson => renderLessonBlock(lesson, dayIdx))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </>
    )
  }

  function renderMonthView() {
    const year = cursor.getFullYear()
    const month = cursor.getMonth()
    const firstDay = new Date(year, month, 1)

    // Build grid starting from the Sunday on or before the first of the month
    const gridStart = new Date(firstDay)
    gridStart.setDate(gridStart.getDate() - gridStart.getDay())

    const cells: Date[] = []
    const cur = new Date(gridStart)
    while (cells.length < 42) {
      cells.push(new Date(cur))
      cur.setDate(cur.getDate() + 1)
      if (cells.length >= 35 && cur.getMonth() !== month) break
    }

    const today = new Date()

    const lessonsByDay: Record<string, Lesson[]> = {}
    for (const lesson of lessons) {
      const ld = parseISODateToLocal(lesson.start_time)
      const key = formatDateLocal(ld)
      if (!lessonsByDay[key]) lessonsByDay[key] = []
      lessonsByDay[key].push(lesson)
    }

    return (
      <>
        <div className="week-nav">
          <div className="nav-group">
            <Button variant="icon" icon={faChevronLeft}  onClick={prev} title="Previous month" />
            <Button variant="icon" icon={faChevronRight} onClick={next} title="Next month" />
          </div>
          <div className="month-nav-title">
            {MONTH_NAMES[month]} {year}
          </div>
        </div>
        <div className="month-grid">
          {MONTH_DAY_NAMES.map(name => (
            <div key={name} className="month-day-name">{name}</div>
          ))}
          {cells.map((d, i) => {
            const isCurrentMonth = d.getMonth() === month
            const isToday = sameDay(d, today)
            const key = formatDateLocal(d)
            const dayLessons = lessonsByDay[key] || []
            return (
              <div
                key={i}
                className={[
                  'month-day-cell',
                  !isCurrentMonth ? 'month-day-other' : '',
                  isToday ? 'month-day-today' : '',
                ].filter(Boolean).join(' ')}
              >
                <div className="month-day-num">{d.getDate()}</div>
                <div className="month-chips">
                  {dayLessons.slice(0, 3).map(lesson => {
                    const bg = getStatusColor(lesson.status)
                    const textColor = getTextColor(bg)
                    const start = lesson.start_time ? new Date(lesson.start_time) : null
                    const timeStr = start ? start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''
                    return (
                      <div
                        key={lesson.lesson_id}
                        className="month-chip"
                        style={{ background: bg, color: textColor }}
                        title={`${lesson.status ?? 'Lesson'} ${timeStr}`}
                      >
                        {timeStr} {lesson.status ?? 'Lesson'}
                      </div>
                    )
                  })}
                  {dayLessons.length > 3 && (
                    <div className="month-chip-more">+{dayLessons.length - 3} more</div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </>
    )
  }

  return (
    <div className="activity-panel" ref={panelRef}>
      <div className="activity-header">
        <div className="activity-left">
          <div className="today-label">
            {new Date().toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
          </div>
          <Button variant="cal-control" onClick={goToday}>Today</Button>
          <div className="cal-view-tabs">
            {(['month', 'week', 'day'] as CalendarView[]).map(v => (
              <button
                key={v}
                className={`cal-view-tab${view === v ? ' active' : ''}`}
                onClick={() => switchView(v)}
              >
                {v.charAt(0).toUpperCase() + v.slice(1)}
              </button>
            ))}
          </div>
        </div>
        <div className="activity-right">
          {!calendarEditMode ? (
            <Button variant="cal-control" onClick={() => setCalendarEditMode(true)}>Edit</Button>
          ) : (
            <div style={{ display: 'flex', gap: 8 }}>
              <Button variant="cal-save"   icon={faCheck}  onClick={() => setCalendarEditMode(false)} title="Save" />
              <Button variant="cal-cancel" icon={faXmark}  onClick={() => setCalendarEditMode(false)} title="Cancel" />
            </div>
          )}
          <Button variant="primary" icon={faPlus} onClick={() => { setEditingLesson(null); setShowModal(true) }}>New Lesson</Button>
        </div>
      </div>

      {view === 'month' && renderMonthView()}
      {view === 'week' && renderTimeGrid(viewDays, WEEK_DAY_NAMES)}
      {view === 'day' && renderTimeGrid(
        viewDays,
        [cursor.toLocaleDateString(undefined, { weekday: 'long' })]
      )}

      {showModal && (
        <ScheduleLessonModal
          existingLesson={editingLesson || undefined}
          onSaved={() => {
            fetchLessons().then(() => {
              if (onLessonCreated) onLessonCreated()
            })
          }}
          onClose={() => {
            setShowModal(false)
            setEditingLesson(null)
            fetchLessons().then(() => {
              if (onLessonCreated) onLessonCreated()
            })
          }}
        />
      )}
    </div>
  )
}

export default LessonCalendar
