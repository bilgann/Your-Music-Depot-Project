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
import React from 'react'
import LessonCalendar from '../components/scheduling/LessonCalendar'

const SchedulePage: React.FC = () => {
    return (
        <div>
           <h1>Schedule</h1>
             <LessonCalendar
                onLessonCreated={() => {
                   console.log('Lesson created/updated')
                }}/>
        </div>
    )
}

export default SchedulePage
