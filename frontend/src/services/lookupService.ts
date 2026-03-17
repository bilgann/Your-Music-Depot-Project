import config from '../config'

export type InstructorOption = {
  instructor_id: number
  full_name: string
  email: string
}

export type StudentOption = {
  student_id: number
  full_name: string
  email: string
}

export type RoomOption = {
  room_id: number
  capacity: number
  instrument_type: string
}

async function parseJsonOrThrow(res: Response) {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }
  return res.json()
}

export async function getInstructors(): Promise<InstructorOption[]> {
  const res = await fetch(`${config.API_BASE}/instructors`)
  return parseJsonOrThrow(res)
}

export async function getStudents(): Promise<StudentOption[]> {
  const res = await fetch(`${config.API_BASE}/students`)
  return parseJsonOrThrow(res)
}

export async function getRooms(): Promise<RoomOption[]> {
  const res = await fetch(`${config.API_BASE}/rooms`)
  return parseJsonOrThrow(res)
}

export async function getInstruments(): Promise<string[]> {
  try {
    const res = await fetch(`${config.API_BASE}/instruments`)
    if (res.ok) {
      const data = await res.json()
      if (Array.isArray(data)) {
        return data.map((item) => (typeof item === 'string' ? item : item.instrument)).filter(Boolean)
      }
    }
  } catch {
    // fallback below
  }

  const rooms = await getRooms()
  return Array.from(new Set(rooms.map((room) => room.instrument_type))).sort()
}