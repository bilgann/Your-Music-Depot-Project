import { apiFetch } from "@/lib/api";

export type CourseRate = {
    charge_type: "one_time" | "hourly";
    amount: number;
    currency?: string;
};

export type CourseInstrument = {
    name: string;
    family: "keyboard" | "strings" | "woodwind" | "brass" | "percussion" | "voice" | "other";
};

export type CourseSkillRange = {
    min_level: string;
    max_level: string;
};

export type Course = {
    course_id: string;
    name: string;
    description: string | null;
    room_id: string;
    instructor_ids: string[];
    student_ids: string[];
    period_start: string;
    period_end: string;
    recurrence: string;
    start_time: string;
    end_time: string;
    rate: CourseRate | null;
    required_instruments: CourseInstrument[];
    capacity: number | null;
    skill_range: CourseSkillRange | null;
    status: string;
};

export type CourseOccurrence = {
    occurrence_id: string;
    course_id: string | null;
    date: string;
    start_time: string;
    end_time: string;
    instructor_id: string;
    room_id: string;
    status: string;
    rate: CourseRate | null;
};

type CoursePayload = {
    name: string;
    room_id: string;
    instructor_ids: string[];
    recurrence: string;
    start_time: string;
    end_time: string;
    period_start: string;
    period_end: string;
    description?: string;
    rate?: CourseRate;
    required_instruments?: CourseInstrument[];
    capacity?: number;
    skill_range?: CourseSkillRange;
    status?: string;
};

function unwrapOne<T>(data: T | T[]): T {
    return Array.isArray(data) ? data[0] : data;
}

export async function listCourses(): Promise<Course[]> {
    const res = await apiFetch("/api/courses");
    if (!res.ok) throw new Error(`Failed to fetch courses: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getCourseById(courseId: string): Promise<Course> {
    const res = await apiFetch(`/api/courses/${courseId}`);
    if (!res.ok) throw new Error(`Failed to fetch course: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}

export async function createCourse(data: CoursePayload): Promise<Course> {
    const res = await apiFetch("/api/courses", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create course: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}

export async function updateCourse(courseId: string, data: Partial<CoursePayload>): Promise<Course> {
    const res = await apiFetch(`/api/courses/${courseId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to update course: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}

export async function deleteCourse(courseId: string): Promise<void> {
    const res = await apiFetch(`/api/courses/${courseId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete course: ${res.statusText}`);
}

export async function projectCourseSchedule(courseId: string): Promise<CourseOccurrence[]> {
    const res = await apiFetch(`/api/courses/${courseId}/project`, { method: "POST" });
    if (!res.ok) throw new Error(`Failed to project course schedule: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function enrollStudentInCourse(courseId: string, studentId: string): Promise<Course> {
    const res = await apiFetch(`/api/courses/${courseId}/students`, {
        method: "POST",
        body: JSON.stringify({ student_id: studentId }),
    });
    if (!res.ok) throw new Error(`Failed to enroll student: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}

export async function unenrollStudentFromCourse(courseId: string, studentId: string): Promise<Course> {
    const res = await apiFetch(`/api/courses/${courseId}/students/${studentId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to unenroll student: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}

export async function addInstructorToCourse(courseId: string, instructorId: string): Promise<Course> {
    const res = await apiFetch(`/api/courses/${courseId}/instructors`, {
        method: "POST",
        body: JSON.stringify({ instructor_id: instructorId }),
    });
    if (!res.ok) throw new Error(`Failed to add instructor: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}

export async function removeInstructorFromCourse(courseId: string, instructorId: string): Promise<Course> {
    const res = await apiFetch(`/api/courses/${courseId}/instructors/${instructorId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to remove instructor: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Course>(body.data);
}