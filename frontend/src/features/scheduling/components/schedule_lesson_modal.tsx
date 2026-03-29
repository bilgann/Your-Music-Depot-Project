'use client'

import React, { useState, useEffect } from 'react'
import { Lesson, Instructor, Room } from '../../../types/index'
import { createLesson, updateLesson } from '../api/lesson'
import { apiJson } from '@/lib/api'
import Button from '@/components/ui/button'

interface ScheduleLessonModalProps {
  existingLesson?: Lesson
  onSaved: () => void
  onClose: () => void
}

const ScheduleLessonModal: React.FC<ScheduleLessonModalProps> = ({ existingLesson, onSaved, onClose }) => {
  const [instructors, setInstructors] = useState<Instructor[]>([])
  const [rooms, setRooms] = useState<Room[]>([])

  const [formData, setFormData] = useState({
    instructor_id: existingLesson?.instructor_id || '',
    room_id: existingLesson?.room_id || '',
    start_time: existingLesson?.start_time ? existingLesson.start_time.slice(0, 16) : '',
    end_time: existingLesson?.end_time ? existingLesson.end_time.slice(0, 16) : '',
    status: existingLesson?.status || 'Scheduled',
    rate: existingLesson?.rate?.toString() || '',
  })

  useEffect(() => {
    apiJson<Instructor[]>('/api/instructors').then(setInstructors).catch(() => {})
    apiJson<Room[]>('/api/rooms').then(setRooms).catch(() => {})
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const start = new Date(formData.start_time)
    const end = new Date(formData.end_time)

    if (!Number.isFinite(start.getTime()) || !Number.isFinite(end.getTime())) {
      alert('Please provide valid start and end times')
      return
    }

    // Saturday support: the studio accepts lessons from 9:00 to 15:00 on Saturdays.
    if (start.getDay() === 6 || end.getDay() === 6) {
      const startHour = start.getHours() + start.getMinutes() / 60
      const endHour = end.getHours() + end.getMinutes() / 60
      if (startHour < 9 || endHour > 15) {
        alert('Saturday lessons must be scheduled between 9:00 AM and 3:00 PM')
        return
      }
    }

    try {
      const payload: Partial<Lesson> = {
        instructor_id: formData.instructor_id,
        room_id: formData.room_id,
        start_time: formData.start_time,
        end_time: formData.end_time,
        status: formData.status,
      }
      if (formData.rate) payload.rate = parseFloat(formData.rate)

      if (existingLesson) {
        await updateLesson(existingLesson.lesson_id, payload)
      } else {
        await createLesson(payload)
      }
      onSaved()
      onClose()
    } catch (error) {
      console.error('Error saving lesson:', error)
      alert('Failed to save lesson')
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <h2>{existingLesson ? 'Edit Lesson' : 'Schedule New Lesson'}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label>Instructor</label>
            <select
              value={formData.instructor_id}
              onChange={(e) => setFormData({ ...formData, instructor_id: e.target.value })}
              required
            >
              <option value="">Select instructor</option>
              {instructors.map(inst => (
                <option key={inst.instructor_id} value={inst.instructor_id}>{inst.name}</option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label>Room</label>
            <select
              value={formData.room_id}
              onChange={(e) => setFormData({ ...formData, room_id: e.target.value })}
              required
            >
              <option value="">Select room</option>
              {rooms.map(room => (
                <option key={room.room_id} value={room.room_id}>{room.name}</option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label>Start Time</label>
            <input
              type="datetime-local"
              value={formData.start_time}
              onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              required
            />
          </div>

          <div className="form-field">
            <label>End Time</label>
            <input
              type="datetime-local"
              value={formData.end_time}
              onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              required
            />
          </div>

          <div className="form-field">
            <label>Status</label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
            >
              <option value="Scheduled">Scheduled</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>

          <div className="form-field">
            <label>Rate ($)</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.rate}
              onChange={(e) => setFormData({ ...formData, rate: e.target.value })}
            />
          </div>

          <div className="modal-footer">
            <Button variant="secondary" onClick={onClose}>Cancel</Button>
            <Button variant="primary" type="submit">{existingLesson ? 'Update' : 'Schedule'}</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ScheduleLessonModal
