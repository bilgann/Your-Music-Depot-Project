/*
Handles all API calls related to lessons, such as fetching lesson details, creating new lessons, updating existing lessons, and deleting lessons. This service acts as an intermediary between the frontend components and the backend API, ensuring that all lesson-related data is managed efficiently and consistently across the application.

Example functions:
- getLessons(): Fetches a list of all scheduled lessons.
- createLesson(lessonData): Sends a POST request to create a new lesson with the provided data.
- update
 */
import config from '../config'
import { Lesson } from '../types/index'

export type LessonFilters = {
  instructorID?: number
  roomID?: number
  day?: string // YYYY-MM-DD
}

function extractErrorMessage(raw: unknown): string {
  if (typeof raw === 'string' && raw.trim()) return raw

  if (raw && typeof raw === 'object') {
    const obj = raw as Record<string, unknown>
    if (typeof obj.error === 'string' && obj.error) return obj.error
    if (typeof obj.message === 'string' && obj.message) return obj.message
    if (typeof obj.details === 'string' && obj.details) return obj.details
  }

  return 'Request failed'
}

async function parseError(res: Response): Promise<never> {
  try {
    const data = await res.json()
    throw new Error(extractErrorMessage(data))
  } catch {
    const text = await res.text()
    throw new Error(extractErrorMessage(text) || `Request failed: ${res.status}`)
  }
}

function serializeLessonPayload(data: Partial<Lesson> & Record<string, unknown>) {
  return {
    instructor_id: data.instructorID,
    student_id: data.studentID,
    room_id: data.roomID,
    instrument: data.instrument,
    lesson_type: data.lesson_type,
    start_time: data.start_time,
    end_time: data.end_time,
    day_of_week: data.day_of_week,
    term: data.term,
    status: data.status ?? 'scheduled'
  }
}

export async function getLessons(
  weekStart: string,
  weekEnd: string,
  filters?: LessonFilters
): Promise<Lesson[]> {
  try {
    const params = new URLSearchParams({
      start_date: weekStart,
      end_date: weekEnd
    })

    if (filters?.instructorID) params.set('instructor_id', String(filters.instructorID))
    if (filters?.roomID) params.set('room_id', String(filters.roomID))
    if (filters?.day) params.set('day', filters.day)

    const res = await fetch(`${config.API_BASE}/lessons?${params.toString()}`)
    if (!res.ok) await parseError(res)
    return await res.json()
  } catch (error) {
    console.error('Error fetching lessons:', error)
    throw error
  }
}

export async function createLesson(data: Partial<Lesson> & Record<string, unknown>): Promise<Lesson> {
  try {
    const res = await fetch(`${config.API_BASE}/lessons`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(serializeLessonPayload(data))
    })

    if (!res.ok) await parseError(res)
    return await res.json()
  } catch (error) {
    console.error('Error creating lesson:', error)
    throw error
  }
}

export async function updateLesson(
  lessonID: number,
  data: Partial<Lesson> & Record<string, unknown>
): Promise<Lesson> {
  try {
    const res = await fetch(`${config.API_BASE}/lessons/${lessonID}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(serializeLessonPayload(data))
    })

    if (!res.ok) await parseError(res)
    return await res.json()
  } catch (error) {
    console.error('Error updating lesson:', error)
    throw error
  }
}

export async function deleteLesson(lessonID: number): Promise<void> {
  try {
    const res = await fetch(`${config.API_BASE}/lessons/${lessonID}`, {
      method: 'DELETE'
    })

    if (!res.ok) await parseError(res)
  } catch (error) {
    console.error('[lessonService] Error deleting lesson:', error)
    throw error
  }
}