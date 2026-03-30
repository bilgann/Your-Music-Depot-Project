'use client'

import React, { useEffect, useState, useMemo, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { faPencil, faTrash, faCheck, faXmark, faChevronLeft, faChevronRight, faPlus } from '@fortawesome/free-solid-svg-icons'
import { getOccurrencesInRange, deleteLesson } from '../api/lesson'
import type { CalendarEvent } from '../api/lesson'
import Button from '@/components/ui/button'
import ScheduleLessonModal from './schedule_lesson_modal'
import { useToast } from '@/components/ui/toast'

type CalendarView = 'month' | 'week' | 'day'

const WEEK_DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const MONTH_DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

function parseDateTime(dstr: string): Date {
  if (!dstr) return new Date(NaN)
  // YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(dstr)) {
    const [y, m, d] = dstr.split('-').map(Number)
    return new Date(y, m - 1, d)
  }
  // YYYY-MM-DDTHH:MM or YYYY-MM-DDTHH:MM:SS
  const match = dstr.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})(?::(\d{2}))?/)
  if (match) {
    return new Date(
      Number(match[1]), Number(match[2]) - 1, Number(match[3]),
      Number(match[4]), Number(match[5]), Number(match[6] ?? 0)
    )
  }
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
  const { toast } = useToast()
  const router = useRouter()
  const [view, setView] = useState<CalendarView>('week')
  const [cursor, setCursor] = useState<Date>(startOfWeek(new Date()))
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [showModal, setShowModal] = useState(false)
  const [calendarEditMode, setCalendarEditMode] = useState(false)
  const panelRef = useRef<HTMLDivElement | null>(null)
  const [rowHeightPx, setRowHeightPx] = useState<number>(54)
  const [rowGapPx, setRowGapPx] = useState<number>(0)

  async function fetchEvents() {
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
      const data = await getOccurrencesInRange(start, end)
      setEvents(data)
    } catch (error) {
      console.error('[LessonCalendar] Error fetching occurrences:', error)
    }
  }

  useEffect(() => { fetchEvents() }, [cursor, view])

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
    const dayEvents: CalendarEvent[][] = viewDays.map(() => [])

    for (const ev of events) {
      const ld = parseDateTime(ev.start_time)
      for (let i = 0; i < viewDays.length; i++) {
        if (sameDay(ld, viewDays[i])) {
          dayEvents[i].push(ev)
          break
        }
      }
    }

    for (let dayIdx = 0; dayIdx < viewDays.length; dayIdx++) {
      const evs = dayEvents[dayIdx].map(ev => {
        const start = parseDateTime(ev.start_time)
        const end = parseDateTime(ev.end_time)
        const sHour = isNaN(start.getTime()) ? 9 : start.getHours()
        const sMin = isNaN(start.getTime()) ? 0 : start.getMinutes()
        const eHour = isNaN(end.getTime()) ? (sHour + 1) : end.getHours()
        const eMin = isNaN(end.getTime()) ? 0 : end.getMinutes()
        const startTotal = sHour + sMin / 60
        const endTotal = eHour + eMin / 60
        return { ev, startTotal, endTotal }
      }).sort((a, b) => a.startTotal - b.startTotal)

      const columnsEnd: number[] = []
      for (const item of evs) {
        let placed = false
        for (let ci = 0; ci < columnsEnd.length; ci++) {
          if (columnsEnd[ci] <= item.startTotal) {
            map[item.ev.id] = { col: ci, total: 0 }
            columnsEnd[ci] = item.endTotal
            placed = true
            break
          }
        }
        if (!placed) {
          columnsEnd.push(item.endTotal)
          map[item.ev.id] = { col: columnsEnd.length - 1, total: 0 }
        }
      }
      const totalCols = columnsEnd.length || 1
      for (const item of evs) {
        if (map[item.ev.id]) map[item.ev.id].total = totalCols
      }
    }

    return map
  }, [events, viewDays, view])

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

  function renderEventBlock(ev: CalendarEvent, dayIdx: number) {
    const start = parseDateTime(ev.start_time)
    const end = parseDateTime(ev.end_time)
    const sHour = isNaN(start.getTime()) ? 9 : start.getHours()
    const sMin = isNaN(start.getTime()) ? 0 : start.getMinutes()
    const eHour = isNaN(end.getTime()) ? (sHour + 1) : end.getHours()
    const eMin = isNaN(end.getTime()) ? 0 : end.getMinutes()

    const startTotalHours = sHour + sMin / 60
    const endTotalHours = eHour + eMin / 60
    const visibleStart = 8
    const visibleEnd = 18

    if (endTotalHours <= visibleStart || startTotalHours >= visibleEnd) return null

    const clampedStart = Math.max(startTotalHours, visibleStart)
    const clampedEnd = Math.min(endTotalHours, visibleEnd)
    const durationHours = Math.max(0.25, clampedEnd - clampedStart)

    const totalSlotHeight = rowHeightPx + rowGapPx
    const top = (clampedStart - visibleStart) * totalSlotHeight
    const height = durationHours * totalSlotHeight - rowGapPx

    const bg = getStatusColor(ev.status)
    const textColor = getTextColor(bg)

    const layout = layoutMap[ev.id] || null
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

    const timeLabel = !isNaN(start.getTime())
      ? `${start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}${!isNaN(end.getTime()) ? ' - ' + end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''}`
      : ''

    const detailUrl = ev.lesson_id ? `/scheduling/${ev.lesson_id}` : null

    return (
      <div
        key={ev.id}
        className={`ac-event ac-event-${dayIdx}`}
        style={style}
        title={`${ev.status ?? 'Lesson'} — ${timeLabel}`}
        onClick={() => {
          if (!calendarEditMode && detailUrl) router.push(detailUrl)
        }}
      >
        <div className="ac-event-name" style={{ fontWeight: 'bold' }}>
          {ev.status ?? 'Lesson'}
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
                  {events.filter(ev => {
                    const ld = parseDateTime(ev.start_time)
                    return sameDay(ld, d)
                  }).map(ev => renderEventBlock(ev, dayIdx))}
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

    const eventsByDay: Record<string, CalendarEvent[]> = {}
    for (const ev of events) {
      const key = ev.date || formatDateLocal(parseDateTime(ev.start_time))
      if (!eventsByDay[key]) eventsByDay[key] = []
      eventsByDay[key].push(ev)
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
            const dayEvents = eventsByDay[key] || []
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
                  {dayEvents.slice(0, 3).map(ev => {
                    const bg = getStatusColor(ev.status)
                    const textColor = getTextColor(bg)
                    const start = parseDateTime(ev.start_time)
                    const timeStr = !isNaN(start.getTime()) ? start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''
                    const detailUrl = ev.lesson_id ? `/scheduling/${ev.lesson_id}` : null
                    return (
                      <div
                        key={ev.id}
                        className="month-chip"
                        style={{ background: bg, color: textColor }}
                        title={`${ev.status ?? 'Lesson'} ${timeStr}`}
                        onClick={() => { if (detailUrl) router.push(detailUrl) }}
                      >
                        {timeStr} {ev.status ?? 'Lesson'}
                      </div>
                    )
                  })}
                  {dayEvents.length > 3 && (
                    <div className="month-chip-more">+{dayEvents.length - 3} more</div>
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
          <Button variant="primary" icon={faPlus} onClick={() => setShowModal(true)}>New Lesson</Button>
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
          onSaved={() => {
            fetchEvents().then(() => {
              if (onLessonCreated) onLessonCreated()
            })
          }}
          onClose={() => {
            setShowModal(false)
            fetchEvents().then(() => {
              if (onLessonCreated) onLessonCreated()
            })
          }}
        />
      )}
    </div>
  )
}

export default LessonCalendar
