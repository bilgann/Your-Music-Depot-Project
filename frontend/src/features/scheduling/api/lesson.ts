/**
 * Lesson API — all calls go through the centralised apiFetch wrapper,
 * which handles Authorization headers and 401 redirects automatically.
 */
import { apiFetch, apiJson } from "@/lib/api";
import type { Lesson } from "@/types/index";

export type OccurrenceEnrollment = {
    enrollment_id: string;
    student_id: string;
    student_name: string;
    attendance_status: string | null;
};

export type LessonOccurrence = {
    occurrence_id: string;
    lesson_id: string | null;
    course_id?: string | null;
    date: string;
    start_time: string;
    end_time: string;
    instructor_id: string;
    room_id: string;
    status: string;
    rate?: number | null;
    enrollments?: OccurrenceEnrollment[];
};

export async function getLessons(weekStart: string, weekEnd: string): Promise<Lesson[]> {
    const res = await apiFetch(
        `/api/lessons?weekStart=${weekStart}&weekEnd=${weekEnd}`
    );
    if (!res.ok) throw new Error(`Failed to fetch lessons: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getLessonById(lessonId: string): Promise<Lesson> {
    return apiJson<Lesson>(`/api/lessons/${lessonId}`);
}

export async function createLesson(data: Partial<Lesson>): Promise<Lesson> {
    const res = await apiFetch("/api/lessons", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`Failed to create lesson: ${res.status} ${err}`);
    }
    const body = await res.json();
    return body.data;
}

export async function updateLesson(lessonId: string, data: Partial<Lesson>): Promise<Lesson> {
    const res = await apiFetch(`/api/lessons/${lessonId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`Failed to update lesson: ${res.status} ${err}`);
    }
    const body = await res.json();
    return body.data;
}

export async function deleteLesson(lessonId: string): Promise<void> {
    const res = await apiFetch(`/api/lessons/${lessonId}`, { method: "DELETE" });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`Failed to delete lesson: ${res.status} ${err}`);
    }
}

export async function projectLessonSchedule(lessonId: string): Promise<LessonOccurrence[]> {
    return apiJson<LessonOccurrence[]>(`/api/lessons/${lessonId}/project`, { method: "POST" });
}

export async function getOccurrenceStudents(occurrenceId: string): Promise<Array<{
    enrollment_id: string;
    student_id: string;
    attendance_status: string | null;
}>> {
    return apiJson(`/api/lessons/occurrences/${occurrenceId}/students`);
}

export async function enrollInOccurrence(occurrenceId: string, studentId: string): Promise<void> {
    const res = await apiFetch(`/api/lessons/occurrences/${occurrenceId}/enroll`, {
        method: "POST",
        body: JSON.stringify({ student_id: studentId }),
    });
    if (!res.ok) throw new Error(`Failed to enroll student: ${res.statusText}`);
}

export async function unenrollFromOccurrence(occurrenceId: string, studentId: string): Promise<void> {
    const res = await apiFetch(`/api/lessons/occurrences/${occurrenceId}/enroll/${studentId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to unenroll student: ${res.statusText}`);
}

export async function recordAttendance(occurrenceId: string, studentId: string, attendanceStatus: string): Promise<void> {
    const res = await apiFetch(`/api/lessons/occurrences/${occurrenceId}/enroll/${studentId}/attendance`, {
        method: "PUT",
        body: JSON.stringify({ attendance_status: attendanceStatus }),
    });
    if (!res.ok) throw new Error(`Failed to record attendance: ${res.statusText}`);
}
