/*
Scheduling Logic

The system needs to enforce these constraints:
A lesson is valid only if:

Instructor
    teaches the instrument
    student's skill ≥ instructor's minimum level
Room
    room supports the instrument
    capacity fits lesson type (private/group)
Time
    instructor not already teaching
    room not already booked
    student not already booked

Calendar Loading Flow
    LessonCalendar.tsx
            ↓
    lessonService.getLessons()
            ↓
    GET /api/lessons?weekStart
            ↓
    lesson_routes.py
            ↓
    lesson_repository.py
            ↓
    LESSON table
            ↓
    Return lessons
            ↓
    Calendar renders events
*/

import React, { useEffect, useState, useMemo, useRef } from 'react'
import { Lesson } from '../../types/index'  // ← FIX: Correct import path
import { getLessons, deleteLesson } from '../../services/lessonService'  // ← FIX: Correct import path
import ScheduleLessonModal from './ScheduleLessonModal'
import '../../styles/Activity.css'  // ← FIX: Correct import path

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
    const map: Record<number, { col: number, total: number }> = {}
    const days: Lesson[][] = [[], [], [], [], []]
    
    for (const lesson of lessons) {
      const ld = parseISODateToLocal(lesson.date)
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
            map[item.lesson.lessonID] = { col: ci, total: 0 }
            columnsEnd[ci] = item.endTotal
            placed = true
            break
          }
        }
        if (!placed) {
          columnsEnd.push(item.endTotal)
          map[item.lesson.lessonID] = { col: columnsEnd.length - 1, total: 0 }
        }
      }
      const totalCols = columnsEnd.length || 1
      for (const item of evs) {
        if (map[item.lesson.lessonID]) map[item.lesson.lessonID].total = totalCols
      }
    }

    return map
  }, [lessons])

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

  function getInstrumentColor(instrument: string): string {
    const colors: Record<string, string> = {
      'Piano': '#C3E4FF',
      'Guitar': '#C3FFD7',
      'Violin': '#FC8C37',
      'Drums': '#F6254F',
      'Voice': '#27608F',
      'Bass': '#FFED7A'
    }
    return colors[instrument] || '#cfe9ff'
  }

  function getTextColor(bg: string): string {
    const textForBg: Record<string, string> = {
      '#C3E4FF': '#0B3A66',
      '#C3FFD7': '#0B6B3B',
      '#FC8C37': '#7A4300',
      '#F6254F': '#7A071F',
      '#27608F': '#07293F',
      '#FFED7A': '#7A5D00'
    }
    return textForBg[bg] || '#000'
  }

  async function handleDeleteLesson(lessonID: number) {
    if (!confirm('Delete this lesson?')) return
    
    try {
      await deleteLesson(lessonID)
      await fetchLessons()
      if (onLessonCreated) onLessonCreated()
    } catch (error) {
      console.error('[LessonCalendar] Delete error:', error)
      alert('Failed to delete lesson')
    }
  }

  function renderLesson(lesson: Lesson) {
    const lessonDate = parseISODateToLocal(lesson.date)
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

    const bg = getInstrumentColor(lesson.instrument)
    const textColor = getTextColor(bg)

    const layout = layoutMap[lesson.lessonID] || null
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

    return (
      <div
        key={lesson.lessonID}
        className={`ac-event ac-event-${dayIdx}`}
        style={style}
        title={`${lesson.instrument} - ${lesson.instructorName || 'Instructor'}`}
      >
        {calendarEditMode && (
          <div className="event-btns-wrapper" style={{ position: 'absolute', top: 6, right: 6, zIndex: 60 }}>
            <button
              className="event-edit-btn"
              onClick={(e) => {
                e.stopPropagation()
                setEditingLesson(lesson)
                setShowModal(true)
              }}
              aria-label="Edit lesson"
            >
              ✎
            </button>
            <button
              className="event-delete-btn"
              onClick={(e) => {
                e.stopPropagation()
                handleDeleteLesson(lesson.lessonID)
              }}
              aria-label="Delete lesson"
            >
              ✕
            </button>
          </div>
        )}
        <div className="ac-event-name" style={{ fontWeight: 'bold' }}>
          {lesson.instrument}
        </div>
        <div style={{ fontSize: '0.85rem', marginTop: 2 }}>
          {lesson.instructorName || 'Instructor'}
        </div>
        {lesson.roomName && (
          <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>
            Room: {lesson.roomName}
          </div>
        )}
        <div className="ac-event-time" style={{ fontSize: '0.8rem', marginTop: 4 }}>
          {start ? `${start.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })} - ${end ? end.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : ''}` : ''}
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
          <button className="today-button" onClick={goToday}>Today</button>
        </div>
        <div className="activity-right">
          {!calendarEditMode ? (
            <button className="edit-cal-btn" onClick={() => setCalendarEditMode(true)}>Edit</button>
          ) : (
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="top-save-btn" onClick={() => setCalendarEditMode(false)} aria-label="Save">✓</button>
              <button className="top-cancel-btn" onClick={() => setCalendarEditMode(false)} aria-label="Cancel">✕</button>
            </div>
          )}
          <button className="new-button" onClick={() => { setEditingLesson(null); setShowModal(true) }}>
            <span className="plus">+</span>New Lesson
          </button>
        </div>
      </div>

      <div className="week-nav">
        <div className="nav-group">
          <button className="nav-btn" onClick={prevWeek} aria-label="Previous week">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15.8333 10.0001H4.16663M4.16663 10.0001L9.99996 15.8334M4.16663 10.0001L9.99996 4.16675" stroke="#5B5B5B" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <button className="nav-btn" onClick={nextWeek} aria-label="Next week">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4.16671 10.0001H15.8334M15.8334 10.0001L10 15.8334M15.8334 10.0001L10 4.16675" stroke="#5B5B5B" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
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
                  const ld = parseISODateToLocal(lesson.date)
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