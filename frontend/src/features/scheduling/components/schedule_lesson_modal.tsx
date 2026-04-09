'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import type { Lesson, Instructor, Room, Student } from '@/types/index'
import { createLesson, updateLesson } from '../api/lesson'
import { apiJson } from '@/lib/api'
import { checkCompatibility, getCompatibleInstructors } from '@/features/students/api/compatibility'
import type { CompatibleInstructor } from '@/features/students/api/compatibility'
import type { RoomDetail } from '@/features/rooms/api/room_detail'
import { getRoomById } from '@/features/rooms/api/room_detail'
import Modal from '@/components/ui/modal'
import MultiSelect from '@/components/ui/multi_select'
import { SelectField, NumberField, TextField } from '@/components/ui/fields'
import RecurrencePicker from '@/components/ui/recurrence_picker'
import { useToast } from '@/components/ui/toast'

interface Props {
  existingLesson?: Lesson
  onSaved: () => void
  onClose: () => void
}

const INSTRUMENT_FAMILY_OPTIONS = [
  { value: 'keyboard', label: 'Keyboard' },
  { value: 'strings', label: 'Strings' },
  { value: 'woodwind', label: 'Woodwind' },
  { value: 'brass', label: 'Brass' },
  { value: 'percussion', label: 'Percussion' },
  { value: 'voice', label: 'Voice' },
  { value: 'other', label: 'Other' },
]

export default function ScheduleLessonModal({ existingLesson, onSaved, onClose }: Props) {
  const { toast } = useToast()
  const [instructors, setInstructors] = useState<Instructor[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [saving, setSaving] = useState(false)

  // Compatibility state
  const [compatibleInstructorIds, setCompatibleInstructorIds] = useState<Set<string> | null>(null)
  const [compatibleStudentIds, setCompatibleStudentIds] = useState<Set<string> | null>(null)
  const [loadingCompat, setLoadingCompat] = useState(false)

  // Room detail for capacity + instruments
  const [roomDetail, setRoomDetail] = useState<RoomDetail | null>(null)

  const [formData, setFormData] = useState({
    instructor_id: existingLesson?.instructor_id || '',
    room_id: existingLesson?.room_id || '',
    start_time: existingLesson?.start_time ? existingLesson.start_time.slice(11, 16) : '',
    end_time: existingLesson?.end_time ? existingLesson.end_time.slice(11, 16) : '',
    status: existingLesson?.status || 'Scheduled',
    rate: existingLesson?.rate?.toString() || '',
    recurrence: existingLesson?.recurrence || '',
    period_start: '',
    period_end: '',
    student_ids: existingLesson?.student_ids ?? [],
    instrument_name: existingLesson?.instrument?.name || '',
    instrument_family: existingLesson?.instrument?.family || '',
    capacity: existingLesson?.capacity?.toString() || '',
  })

  useEffect(() => {
    Promise.all([
      apiJson<Instructor[]>('/api/instructors'),
      apiJson<Room[]>('/api/rooms'),
      apiJson<Student[]>('/api/students'),
    ]).then(([i, r, s]) => {
      setInstructors(i)
      setRooms(r)
      setStudents(s)
    }).catch(() => {})
  }, [])

  // Fetch room detail when room changes (for capacity + available instruments)
  useEffect(() => {
    if (!formData.room_id) { setRoomDetail(null); return }
    getRoomById(formData.room_id).then(setRoomDetail).catch(() => setRoomDetail(null))
  }, [formData.room_id])

  const roomCapacity = roomDetail?.capacity ?? null

  // Room instrument options for the instrument selector
  const roomInstrumentOptions = useMemo(() => {
    if (!roomDetail?.instruments?.length) return []
    return roomDetail.instruments.map((i) => ({
      value: `${i.name}|${i.family}`,
      label: `${i.name} (${i.family})${i.quantity ? ` — ${i.quantity} available` : ''}`,
    }))
  }, [roomDetail])

  // When instructor changes → check which students are compatible
  const checkStudentCompatibility = useCallback(async (instructorId: string) => {
    if (!instructorId) { setCompatibleStudentIds(null); return }
    setLoadingCompat(true)
    try {
      const results = await Promise.all(
        students.map(async (s) => {
          try {
            const result = await checkCompatibility(s.student_id, instructorId)
            return { studentId: s.student_id, compatible: result.can_assign }
          } catch {
            return { studentId: s.student_id, compatible: true }
          }
        })
      )
      setCompatibleStudentIds(new Set(results.filter((r) => r.compatible).map((r) => r.studentId)))
    } catch {
      setCompatibleStudentIds(null)
    } finally {
      setLoadingCompat(false)
    }
  }, [students])

  // When students change → find instructors compatible with ALL selected students
  const checkInstructorCompatibility = useCallback(async (studentIds: string[]) => {
    if (studentIds.length === 0) { setCompatibleInstructorIds(null); return }
    setLoadingCompat(true)
    try {
      const perStudent = await Promise.all(
        studentIds.map(async (sid) => {
          try {
            const compatibles = await getCompatibleInstructors(sid)
            return new Set(compatibles.map((c: CompatibleInstructor) => c.instructor_id))
          } catch {
            return null
          }
        })
      )
      // Intersect: instructor must be compatible with ALL students
      const sets = perStudent.filter(Boolean) as Set<string>[]
      if (sets.length === 0) { setCompatibleInstructorIds(null); return }
      const intersection = new Set([...sets[0]].filter((id) => sets.every((s) => s.has(id))))
      setCompatibleInstructorIds(intersection)
    } catch {
      setCompatibleInstructorIds(null)
    } finally {
      setLoadingCompat(false)
    }
  }, [])

  // Run compatibility checks when instructor or students change
  useEffect(() => {
    if (students.length > 0 && formData.instructor_id) {
      void checkStudentCompatibility(formData.instructor_id)
    }
  }, [formData.instructor_id, students, checkStudentCompatibility])

  useEffect(() => {
    void checkInstructorCompatibility(formData.student_ids)
  }, [formData.student_ids, checkInstructorCompatibility])

  // Filtered options based on compatibility
  const instructorOptions = useMemo(() => {
    if (compatibleInstructorIds === null) {
      return instructors.map((i) => ({ value: i.instructor_id, label: i.name }))
    }
    return instructors
      .filter((i) => compatibleInstructorIds.has(i.instructor_id))
      .map((i) => ({ value: i.instructor_id, label: i.name }))
  }, [instructors, compatibleInstructorIds])

  const studentOptions = useMemo(() => {
    if (compatibleStudentIds === null) {
      return students.map((s) => ({ value: s.student_id, label: s.person.name }))
    }
    return students
      .filter((s) => compatibleStudentIds.has(s.student_id))
      .map((s) => ({ value: s.student_id, label: s.person.name }))
  }, [students, compatibleStudentIds])

  const roomOptions = useMemo(
    () => rooms.map((r) => ({
      value: r.room_id,
      label: r.name + (r.capacity ? ` (cap: ${r.capacity})` : ''),
    })),
    [rooms]
  )

  const selectedInstrument = formData.instrument_name && formData.instrument_family
    ? `${formData.instrument_name}|${formData.instrument_family}`
    : ''

  function handleInstrumentChange(value: string) {
    if (!value) {
      setFormData({ ...formData, instrument_name: '', instrument_family: '' })
      return
    }
    const [name, family] = value.split('|')
    setFormData({ ...formData, instrument_name: name, instrument_family: family })
  }

  function handleRoomChange(roomId: string) {
    setFormData({ ...formData, room_id: roomId, instrument_name: '', instrument_family: '' })
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!formData.start_time || !formData.end_time) {
      alert('Please provide valid start and end times')
      return
    }

    // Saturday support: the studio accepts lessons from 9:00 to 15:00 on Saturdays.
    // Only applies to one-time lessons where we know the specific date.
    const isOneTimeDate = formData.recurrence && !formData.recurrence.includes(' ')
    if (isOneTimeDate) {
      const lessonDate = new Date(`${formData.recurrence}T${formData.start_time}`)
      if (lessonDate.getDay() === 6) {
        const [startH, startM] = formData.start_time.split(':').map(Number)
        const [endH, endM] = formData.end_time.split(':').map(Number)
        if ((startH + startM / 60) < 9 || (endH + endM / 60) > 15) {
          alert('Saturday lessons must be scheduled between 9:00 AM and 3:00 PM')
          return
        }
      }
    }

    setSaving(true)
    try {
      const payload: Partial<Lesson> = {
        instructor_id: formData.instructor_id,
        room_id: formData.room_id,
        start_time: formData.start_time,
        end_time: formData.end_time,
        status: formData.status,
        student_ids: formData.student_ids,
      }
      if (formData.rate) payload.rate = parseFloat(formData.rate)
      if (formData.recurrence) payload.recurrence = formData.recurrence
      if (formData.capacity) payload.capacity = parseInt(formData.capacity)

      if (existingLesson) {
        await updateLesson(existingLesson.lesson_id, payload)
      } else {
        await createLesson(payload)
      }
      onSaved()
      onClose()
    } catch (error) {
      console.error('Error saving lesson:', error)
      toast('Failed to save lesson', 'error')
    } finally {
      setSaving(false)
    }
  }

  const lessonCapacity = formData.capacity ? parseInt(formData.capacity) : null
  const effectiveCapacity = lessonCapacity ?? roomCapacity
  const capacityHint = effectiveCapacity
    ? `${formData.student_ids.length} of ${effectiveCapacity} spots filled`
    : undefined
  const overCapacity = effectiveCapacity !== null && formData.student_ids.length > effectiveCapacity

  return (
    <Modal
      title={existingLesson ? 'Edit Lesson' : 'Schedule New Lesson'}
      onClose={onClose}
      onSubmit={handleSubmit}
      submitLabel={existingLesson ? 'Update' : 'Schedule'}
      saving={saving}
    >
      <SelectField
        label="Room"
        value={formData.room_id}
        onChange={handleRoomChange}
        options={roomOptions}
        required
      />

      {roomInstrumentOptions.length > 0 && (
        <SelectField
          label="Instrument"
          value={selectedInstrument}
          onChange={handleInstrumentChange}
          options={roomInstrumentOptions}
          placeholder="Select instrument..."
          required
        />
      )}
      <div style={{ display: roomInstrumentOptions.length > 0 ? 'none' : 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <TextField
          label="Instrument Name"
          value={formData.instrument_name}
          onChange={(v) => setFormData(prev => ({ ...prev, instrument_name: v }))}
        />
        <SelectField
          label="Instrument Family"
          value={formData.instrument_family}
          onChange={(v) => setFormData(prev => ({ ...prev, instrument_family: v }))}
          options={INSTRUMENT_FAMILY_OPTIONS}
          placeholder="Select family..."
        />
      </div>

      <SelectField
        label="Instructor"
        value={formData.instructor_id}
        onChange={(v) => setFormData({ ...formData, instructor_id: v })}
        options={instructorOptions}
        required
      />

      <MultiSelect
        label="Students"
        options={studentOptions}
        selected={formData.student_ids}
        onChange={(student_ids) => setFormData({ ...formData, student_ids })}
        max={effectiveCapacity ?? undefined}
        hint={
          loadingCompat
            ? 'Checking compatibility...'
            : overCapacity
              ? `Over capacity! Lesson holds ${effectiveCapacity} students.`
              : capacityHint
        }
      />

      <RecurrencePicker
        value={formData.recurrence}
        onChange={(v) => setFormData({ ...formData, recurrence: v })}
        periodStart={formData.period_start}
        periodEnd={formData.period_end}
        onPeriodChange={(start, end) => setFormData({ ...formData, period_start: start, period_end: end })}
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div className="form-field">
          <label>Start Time</label>
          <input
            type="time"
            value={formData.start_time}
            onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
            required
          />
        </div>
        <div className="form-field">
          <label>End Time</label>
          <input
            type="time"
            value={formData.end_time}
            onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
            required
          />
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
        <SelectField
          label="Status"
          value={formData.status}
          onChange={(v) => setFormData({ ...formData, status: v })}
          options={[
            { value: 'Scheduled', label: 'Scheduled' },
            { value: 'Completed', label: 'Completed' },
            { value: 'Cancelled', label: 'Cancelled' },
          ]}
        />
        <NumberField
          label="Rate ($)"
          value={formData.rate}
          onChange={(v) => setFormData({ ...formData, rate: v })}
          min={0}
          step={0.01}
        />
        <NumberField
          label="Capacity"
          value={formData.capacity}
          onChange={(v) => setFormData({ ...formData, capacity: v })}
          min={1}
          placeholder={roomCapacity ? `Room max: ${roomCapacity}` : undefined}
        />
      </div>
    </Modal>
  )
}
