'use client'

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

import React, { useState, useEffect } from 'react'
import { Lesson } from '../../../types/index'
import { createLesson, updateLesson } from '../api/lesson'

interface ScheduleLessonModalProps {
  existingLesson?: Lesson
  onSaved: () => void
  onClose: () => void
}

const ScheduleLessonModal: React.FC<ScheduleLessonModalProps> = ({ existingLesson, onSaved, onClose }) => {
  const [formData, setFormData] = useState({
    instructorID: existingLesson?.instructorID || 0,
    studentID: existingLesson?.studentID || 0,
    roomID: existingLesson?.roomID || 0,
    instrument: existingLesson?.instrument || '',
    lesson_type: existingLesson?.lesson_type || 'private',
    date: existingLesson?.date || '',
    start_time: existingLesson?.start_time || '',
    end_time: existingLesson?.end_time || '',
    status: existingLesson?.status || 'scheduled'
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    try {
      if (existingLesson) {
        await updateLesson(existingLesson.lessonID, formData)
      } else {
        await createLesson(formData)
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
          <div>
            <label>Instrument:</label>
            <input
              type="text"
              value={formData.instrument}
              onChange={(e) => setFormData({ ...formData, instrument: e.target.value })}
              required
            />
          </div>
          
          <div>
            <label>Date:</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
            />
          </div>

          <div>
            <label>Start Time:</label>
            <input
              type="datetime-local"
              value={formData.start_time}
              onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              required
            />
          </div>

          <div>
            <label>End Time:</label>
            <input
              type="datetime-local"
              value={formData.end_time}
              onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              required
            />
          </div>

          <div className="modal-buttons">
            <button type="submit">Save</button>
            <button type="button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ScheduleLessonModal