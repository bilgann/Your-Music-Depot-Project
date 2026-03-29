'use client'

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
import Navbar from '@/components/ui/navbar'
import LessonCalendar from '../../../features/scheduling/components/lesson_calendar'

export default function SchedulePage() {
    return (
        <>
            <Navbar title="Schedule" className="page-schedule" />
            <LessonCalendar
                onLessonCreated={() => {
                    console.log('Lesson created/updated')
                }}/>
        </>
    )
}
