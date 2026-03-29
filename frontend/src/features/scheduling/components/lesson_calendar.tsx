'use client'

import React, { useEffect, useState, useMemo, useRef } from 'react'
import { faPencil, faTrash, faCheck, faXmark, faChevronLeft, faChevronRight, faPlus } from '@fortawesome/free-solid-svg-icons'
import { Lesson } from '../../../types/index'
import { getLessons, deleteLesson } from '../api/lesson'
import Button from '@/components/ui/button'
import ScheduleLessonModal from './schedule_lesson_modal'

const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

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
  const [weekStart, setWeekStart] = useState<Date>(startOfWeek(new Date()))
  const [lessons, setLessons] = useState<Lesson[]>([])
  const [showModal, setShowModal] = useState(false)
  const [calendarEditMode, setCalendarEditMode] = useState(false)
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null)
  const panelRef = useRef<HTMLDivElement | null>(null)
  const [rowHeightPx, setRowHeightPx] = useState<number>(54)
  const [rowGapPx, setRowGapPx] = useState<number>(0)

  async function fetchLessons() {
    function formatDateLocal(d: Date) {
      const y = d.getFullYear()
      const m = String(d.getMonth() + 1).padStart(2, '0')
      const dd = String(d.getDate()).padStart(2, '0')
      return `${y}-${m}-${dd}`
    }

    const start = formatDateLocal(weekStart)
    const end = formatDateLocal(new Date(weekStart.getTime() + 6 * 24 * 60 * 60 * 1000))

    try {
      const data = await getLessons(start, end)
      console.debug('[LessonCalendar] fetched lessons count=', Array.isArray(data) ? data.length : 0)
      setLessons(data)
    } catch (error) {
      console.error('[LessonCalendar] Error fetching lessons:', error)
    }
  }

  useEffect(() => { fetchLessons() }, [weekStart])

  useEffect(() => {
    if (onWeekChange) onWeekChange(weekStart)
  }, [weekStart, onWeekChange])

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

  useEffect(() => {
    const id = setInterval(() => {
      const nowStart = startOfWeek(new Date())
      setWeekStart(prev => {
        if (!prev) return nowStart
        if (prev.getTime() !== nowStart.getTime()) return nowStart
        return prev
      })
    }, 60 * 60 * 1000)

    const nowStart = startOfWeek(new Date())
    setWeekStart(prev => {
      if (!prev) return nowStart
      if (prev.getTime() !== nowStart.getTime()) return nowStart
      return prev
    })

    return () => clearInterval(id)
  }, [])

  const layoutMap = useMemo(() => {
    const map: Record<string, { col: number, total: number }> = {}
    const days: Lesson[][] = [[], [], [], [], []]

    for (const lesson of lessons) {
      const ld = parseISODateToLocal(lesson.start_time)
      const dayIdx = (ld.getDay() === 0 ? 6 : ld.getDay() - 1)
      if (dayIdx >= 0 && dayIdx <= 4) days[dayIdx].push(lesson)
    }

    for (let dayIdx = 0; dayIdx < 5; dayIdx++) {
      const evs = days[dayIdx].map(lesson => {
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
  }, [lessons])

  function prevWeek() {
    setWeekStart(new Date(weekStart.getTime() - 7 * 24 * 60 * 60 * 1000))
  }

  function nextWeek() {
    setWeekStart(new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000))
  }

  function goToday() {
    setWeekStart(startOfWeek(new Date()))
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

  function renderLesson(lesson: Lesson) {
    const lessonDate = parseISODateToLocal(lesson.start_time)
    const dayIdx = (lessonDate.getDay() === 0 ? 6 : lessonDate.getDay() - 1)
    if (dayIdx < 0 || dayIdx > 4) return null

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

  const days = Array.from({ length: 5 }).map((_, i) => {
    const d = new Date(weekStart)
    d.setDate(d.getDate() + i)
    return d
  })

  return (
    <div className="activity-panel" ref={panelRef}>
      <div className="activity-header">
        <div className="activity-left">
          <div className="today-label">
            {new Date().toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
          </div>
          <Button variant="cal-control" onClick={goToday}>Today</Button>
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

      <div className="week-nav">
        <div className="nav-group">
          <Button variant="icon" icon={faChevronLeft}  onClick={prevWeek} title="Previous week" />
          <Button variant="icon" icon={faChevronRight} onClick={nextWeek} title="Next week" />
        </div>
        <div className="days-row">
          {days.map((d, idx) => (
            <div key={idx} className="day-header">
              <div className="day-name">{dayNames[idx]}</div>
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
        <div className="days-col">
          {days.map((d, dayIdx) => (
            <div key={dayIdx} className="day-column">
              <div className="day-grid" style={{ gridTemplateRows: `repeat(${hours.length}, 1fr)` }}>
                {hours.map(h => (
                  <div key={h} className="slot-cell" data-hour={h}></div>
                ))}
                {lessons.filter(lesson => {
                  const ld = parseISODateToLocal(lesson.start_time)
                  return ld.getFullYear() === d.getFullYear() && ld.getMonth() === d.getMonth() && ld.getDate() === d.getDate()
                }).map(lesson => renderLesson(lesson))}
              </div>
            </div>
          ))}
        </div>
      </div>

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
