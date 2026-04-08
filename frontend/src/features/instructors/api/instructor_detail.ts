import { apiFetch } from "@/lib/api";
import type { Lesson } from "@/types/index";
import type { Student } from "@/features/students/api/student";
import type { Instructor } from "@/features/instructors/api/instructor";

export type InstrumentProficiency = {
    name: string;
    family: "keyboard" | "strings" | "woodwind" | "brass" | "percussion" | "voice" | "other";
    min_level: string;
    max_level: string;
};

export type Credential = {
    credential_id: string;
    instructor_id: string;
    credential_type: string;
    proficiencies: InstrumentProficiency[];
    valid_from: string | null;
    valid_until: string | null;
    issued_by?: string | null;
    issued_date?: string | null;
};

export type InstructorDetail = Instructor & {
    hourly_rate?: number | null;
    status?: string | null;
    blocked_times?: Array<{ start_time?: string; end_time?: string; reason?: string | null }>;
};

export type InstructorCompatibility = {
    student_id: string;
    student_name: string;
    can_assign: boolean;
    hard_verdict: string | null;
    soft_verdict: string | null;
    reasons: string[];
};

type CompatibilityResponse = {
    can_assign: boolean;
    hard_verdict: string | null;
    soft_verdict: string | null;
    reasons: string[];
};

function unwrapOne<T>(data: T | T[]): T {
    return Array.isArray(data) ? data[0] : data;
}

export async function getInstructorById(instructorId: string): Promise<InstructorDetail> {
    const res = await apiFetch(`/api/instructors/${instructorId}`);
    if (!res.ok) throw new Error(`Failed to fetch instructor: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<InstructorDetail>(body.data);
}

export async function getInstructorCredentials(instructorId: string): Promise<Credential[]> {
    const res = await apiFetch(`/api/credentials?instructor_id=${encodeURIComponent(instructorId)}`);
    if (!res.ok) throw new Error(`Failed to fetch credentials: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function addCredential(data: {
    instructor_id: string;
    credential_type: string;
    proficiencies?: InstrumentProficiency[];
    issued_by?: string;
    issued_date?: string;
    valid_from?: string;
    valid_until?: string;
}): Promise<Credential> {
    const res = await apiFetch("/api/credentials", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to add credential: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Credential>(body.data);
}

export async function removeCredential(credentialId: string): Promise<void> {
    const res = await apiFetch(`/api/credentials/${credentialId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to remove credential: ${res.statusText}`);
}

export async function getInstructorLessons(): Promise<Lesson[]> {
    const res = await apiFetch("/api/lessons");
    if (!res.ok) throw new Error(`Failed to fetch lessons: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getCoursesByInstructor(instructorId: string): Promise<Array<{ student_ids?: string[] }>> {
    const res = await apiFetch(`/api/courses?instructor_id=${encodeURIComponent(instructorId)}`);
    if (!res.ok) throw new Error(`Failed to fetch instructor courses: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getInstructorCompatibility(studentId: string, instructorId: string): Promise<CompatibilityResponse> {
    const res = await apiFetch(
        `/api/compatibility/check?student_id=${encodeURIComponent(studentId)}&instructor_id=${encodeURIComponent(instructorId)}`
    );
    if (!res.ok) throw new Error(`Failed to fetch compatibility: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export function buildInstructorStudents(courses: Array<{ student_ids?: string[] }>, students: Student[]): Student[] {
    const ids = new Set(courses.flatMap((course) => course.student_ids ?? []));
    return students.filter((student) => ids.has(student.student_id));
}
