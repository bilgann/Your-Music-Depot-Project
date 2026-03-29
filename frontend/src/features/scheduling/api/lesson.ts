/*
Handles all API calls related to lessons, such as fetching lesson details, creating new lessons, updating existing lessons, and deleting lessons. This service acts as an intermediary between the frontend components and the backend API, ensuring that all lesson-related data is managed efficiently and consistently across the application.

Example functions:
- getLessons(): Fetches a list of all scheduled lessons.
- createLesson(lessonData): Sends a POST request to create a new lesson with the provided data.
- update
 */
import config from '../../../config'
import { Lesson } from '../../../types/index'

export async function getLessons(weekStart: string, weekEnd: string): Promise<Lesson[]> {
    try {
        const res = await fetch(`/api/lessons?weekStart=${weekStart}&weekEnd=${weekEnd}`)
        if (!res.ok) {
            throw new Error(`Failed to fetch lessons: ${res.statusText}`)
        }
        return await res.json()  // ← MISSING: Add return statement
    } catch(error) {
        console.error('Error fetching lessons:', error)
        throw error
    }
}

export async function createLesson(data: Partial<Lesson>): Promise<Lesson> {
    try {
        const res = await fetch(`/api/lessons`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })

        if (!res.ok) {
            const error = await res.text()
            throw new Error(`Failed to create lesson: ${res.status} ${error}`)
        }

        return await res.json()

    } catch(error) {
        console.error('Error creating lesson:', error)
        throw error
    }
}

export async function updateLesson(lessonID: number, data: Partial<Lesson>): Promise<Lesson> {
    try {
        const res = await fetch(`/api/lessons/${lessonID}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })

        if (!res.ok) {
            const error = await res.text()
            throw new Error(`Failed to update lesson: ${res.status} ${error}`)
        }

        return await res.json()

    } catch(error) {
        console.error('Error updating lesson:', error)
        throw error
    }
}

export async function deleteLesson(lessonID: number): Promise<void> {
    try {
        const res = await fetch(`/api/lessons/${lessonID}`, {
            method: 'DELETE'
        })

        if (!res.ok) {
            const error = await res.text()
            throw new Error(`Failed to delete lesson: ${res.status} ${error}`)
        }
    } catch (error) {
        console.error('[lessonService] Error deleting lesson:', error)
        throw error
    }
}