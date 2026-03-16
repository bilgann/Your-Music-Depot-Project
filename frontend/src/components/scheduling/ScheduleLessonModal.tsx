/*
The popup where admin schedules a lesson.

Example UI fields:

Student
Instrument
Instructor
Room
Day
Start Time
End Time
Lesson Type

Submit → POST request.
*/

import React, { useEffect, useMemo, useState } from 'react'
import { Lesson } from '../../types/index'
import { createLesson, updateLesson } from '../../services/lessonService'
import {
  getInstructors,
  getStudents,
  getRooms,
  getInstruments,
  InstructorOption,
  StudentOption,
  RoomOption
} from '../../services/lookupService'

interface ScheduleLessonModalProps {
  existingLesson?: Lesson
  onSaved: () => void
  onClose: () => void
}

type FormState = {
  instructorID: number
  studentID: number
  roomID: number
  instrument: string
  lesson_type: string
  lessonDate: string
  startTime: string
  endTime: string
  status: string
}

const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
const lessonTypes = ['private', 'group']

function toTimeInputValue(value?: string | null) {
  if (!value) return ''
  return value.length >= 5 ? value.slice(0, 5) : value
}

function toDateInputValue(value?: string | null) {
  if (!value) return ''
  return value.slice(0, 10)
}

function getTermFromDate(dateStr: string) {
  const month = new Date(`${dateStr}T00:00:00`).getMonth() + 1
  const year = new Date(`${dateStr}T00:00:00`).getFullYear()

  if (month >= 1 && month <= 5) return `${year}-Spring`
  if (month >= 6 && month <= 8) return `${year}-Summer`
  if (month >= 9 && month <= 12) return `${year}-Fall`
  return `${year}-Term`
}

const ScheduleLessonModal: React.FC<ScheduleLessonModalProps> = ({ existingLesson, onSaved, onClose }) => {
  const [formData, setFormData] = useState<FormState>({
    instructorID: existingLesson?.instructorID || 0,
    studentID: existingLesson?.studentID || 0,
    roomID: existingLesson?.roomID || 0,
    instrument: existingLesson?.instrument || '',
    lesson_type: existingLesson?.lesson_type || 'private',
    lessonDate: toDateInputValue(existingLesson?.date),
    startTime: toTimeInputValue(existingLesson?.start_time),
    endTime: toTimeInputValue(existingLesson?.end_time),
    status: existingLesson?.status || 'scheduled'
  })

  const [instructors, setInstructors] = useState<InstructorOption[]>([])
  const [students, setStudents] = useState<StudentOption[]>([])
  const [rooms, setRooms] = useState<RoomOption[]>([])
  const [instruments, setInstruments] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  useEffect(() => {
    async function loadOptions() {
      try {
        setLoading(true)
        setErrorMessage('')

        const [instructorData, studentData, roomData, instrumentData] = await Promise.all([
          getInstructors(),
          getStudents(),
          getRooms(),
          getInstruments()
        ])

        setInstructors(instructorData)
        setStudents(studentData)
        setRooms(roomData)
        setInstruments(instrumentData)
      } catch (error) {
        console.error('Failed to load lesson form options:', error)
        setErrorMessage(error instanceof Error ? error.message : 'Failed to load form options.')
      } finally {
        setLoading(false)
      }
    }

    loadOptions()
  }, [])

  const filteredRooms = useMemo(() => {
    if (!formData.instrument) return rooms
    return rooms.filter((room) => room.instrument_type === formData.instrument)
  }, [rooms, formData.instrument])

  function updateField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setFormData((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErrorMessage('')

    if (!formData.lessonDate) {
      setErrorMessage('Please select a date.')
      return
    }

    if (!formData.startTime || !formData.endTime) {
      setErrorMessage('Please select both start and end times.')
      return
    }

    if (formData.endTime <= formData.startTime) {
      setErrorMessage('End time must be later than start time.')
      return
    }

    const pickedDate = new Date(`${formData.lessonDate}T00:00:00`)
    const payload = {
      instructorID: formData.instructorID,
      studentID: formData.studentID,
      roomID: formData.roomID,
      instrument: formData.instrument,
      lesson_type: formData.lesson_type,
      start_time: `${formData.startTime}:00`,
      end_time: `${formData.endTime}:00`,
      day_of_week: dayNames[pickedDate.getDay()],
      term: getTermFromDate(formData.lessonDate),
      status: formData.status
    }

    try {
      setSubmitting(true)

      if (existingLesson) {
        await updateLesson(existingLesson.lessonID, payload)
      } else {
        await createLesson(payload)
      }

      onSaved()
      onClose()
    } catch (error) {
      console.error('Error saving lesson:', error)
      setErrorMessage(error instanceof Error ? error.message : 'Failed to save lesson.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.45)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
      }}
    >
      <div
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: 640,
          background: '#fff',
          borderRadius: 12,
          padding: 20,
          boxShadow: '0 16px 40px rgba(0,0,0,0.2)'
        }}
      >
        <h2 style={{ marginTop: 0 }}>
          {existingLesson ? 'Edit Lesson' : 'Schedule New Lesson'}
        </h2>

        {errorMessage && (
          <div
            style={{
              marginBottom: 16,
              padding: '10px 12px',
              borderRadius: 8,
              background: '#ffe8e8',
              color: '#9b1c1c',
              border: '1px solid #f5b5b5'
            }}
          >
            {errorMessage}
          </div>
        )}

        {loading ? (
          <p>Loading form options...</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label htmlFor="instrument">Instrument</label>
                <select
                  id="instrument"
                  value={formData.instrument}
                  onChange={(e) => {
                    updateField('instrument', e.target.value)
                    updateField('roomID', 0)
                  }}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                >
                  <option value="">Select instrument</option>
                  {instruments.map((instrument) => (
                    <option key={instrument} value={instrument}>
                      {instrument}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="lesson-type">Lesson Type</label>
                <select
                  id="lesson-type"
                  value={formData.lesson_type}
                  onChange={(e) => updateField('lesson_type', e.target.value)}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                >
                  {lessonTypes.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="instructor">Instructor</label>
                <select
                  id="instructor"
                  value={formData.instructorID}
                  onChange={(e) => updateField('instructorID', Number(e.target.value))}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                >
                  <option value={0}>Select instructor</option>
                  {instructors.map((instructor) => (
                    <option key={instructor.instructor_id} value={instructor.instructor_id}>
                      {instructor.full_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="student">Student</label>
                <select
                  id="student"
                  value={formData.studentID}
                  onChange={(e) => updateField('studentID', Number(e.target.value))}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                >
                  <option value={0}>Select student</option>
                  {students.map((student) => (
                    <option key={student.student_id} value={student.student_id}>
                      {student.full_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="room">Room</label>
                <select
                  id="room"
                  value={formData.roomID}
                  onChange={(e) => updateField('roomID', Number(e.target.value))}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                >
                  <option value={0}>Select room</option>
                  {filteredRooms.map((room) => (
                    <option key={room.room_id} value={room.room_id}>
                      Room #{room.room_id} - {room.instrument_type} (Cap {room.capacity})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="date">Date</label>
                <input
                  id="date"
                  type="date"
                  value={formData.lessonDate}
                  onChange={(e) => updateField('lessonDate', e.target.value)}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                />
              </div>

              <div>
                <label htmlFor="start-time">Start Time</label>
                <input
                  id="start-time"
                  type="time"
                  value={formData.startTime}
                  onChange={(e) => updateField('startTime', e.target.value)}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                />
              </div>

              <div>
                <label htmlFor="end-time">End Time</label>
                <input
                  id="end-time"
                  type="time"
                  value={formData.endTime}
                  onChange={(e) => updateField('endTime', e.target.value)}
                  required
                  style={{ width: '100%', padding: 8, marginTop: 4 }}
                />
              </div>
            </div>

            <div className="modal-buttons" style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 20 }}>
              <button type="button" onClick={onClose} disabled={submitting}>
                Cancel
              </button>
              <button type="submit" disabled={submitting}>
                {submitting ? 'Saving...' : existingLesson ? 'Update Lesson' : 'Create Lesson'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}

export default ScheduleLessonModal