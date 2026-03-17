/*
SCHEDULING PAGE
 
Includes:
- Calendar view of scheduled events
- Option to add new events
- Option to edit or delete existing events

Made by: Bilgan 
Date: 2026-03-09

Data Flow (Very Important)

    When scheduling a lesson:

    ScheduleLessonModal.tsx
            ↓
    lessonService.createLesson()
            ↓
    POST /api/lessons
            ↓
    lesson_routes.py
            ↓
    scheduling_service.py
            ↓
    lesson_repository.py
            ↓
    PostgreSQL
 */
import React, { useState } from 'react'
import LessonCalendar from '../components/scheduling/LessonCalendar'

type ScheduleTab = 'schedule' | 'instructors' | 'students' | 'rooms' | 'instruments'

const SchedulePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ScheduleTab>('schedule')

  return (
    <main className="page-schedule" style={{ padding: '20px' }}>
      <h1>Schedule</h1>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
        <button onClick={() => setActiveTab('schedule')} disabled={activeTab === 'schedule'}>
          Schedule
        </button>
        <button onClick={() => setActiveTab('instructors')} disabled={activeTab === 'instructors'}>
          Instructors
        </button>
        <button onClick={() => setActiveTab('students')} disabled={activeTab === 'students'}>
          Students
        </button>
        <button onClick={() => setActiveTab('rooms')} disabled={activeTab === 'rooms'}>
          Rooms
        </button>
        <button onClick={() => setActiveTab('instruments')} disabled={activeTab === 'instruments'}>
          Instruments
        </button>
      </div>

      {activeTab === 'schedule' && (
        <LessonCalendar
          onLessonCreated={() => {
            console.log('Lesson created/updated')
          }}
        />
      )}

      {activeTab === 'instructors' && (
        <section>
          <h2>Instructors</h2>
          <p>Instructor management content can be placed here.</p>
        </section>
      )}

      {activeTab === 'students' && (
        <section>
          <h2>Students</h2>
          <p>Student management content can be placed here.</p>
        </section>
      )}

      {activeTab === 'rooms' && (
        <section>
          <h2>Rooms</h2>
          <p>Room management content can be placed here.</p>
        </section>
      )}

      {activeTab === 'instruments' && (
        <section>
          <h2>Instruments</h2>
          <p>Instrument management content can be placed here.</p>
        </section>
      )}
    </main>
  )
}

export default SchedulePage