import { apiFetch } from "@/lib/api";

export type CompatibilityCheckResult = {
    can_assign: boolean;
    hard_verdict: string | null;
    soft_verdict: string | null;
    reasons: string[];
};

export type StudentCompatibilityItem = CompatibilityCheckResult & {
    instructor_id: string;
    instructor_name: string;
};

export type CompatibilityOverrideRecord = {
    compatibility_id: string;
    instructor_id: string;
    student_id: string;
    verdict: string;
    reason: string | null;
    initiated_by: string;
};

export async function checkCompatibility(studentId: string, instructorId: string): Promise<CompatibilityCheckResult> {
    const params = new URLSearchParams({ student_id: studentId, instructor_id: instructorId });
    const res = await apiFetch(`/api/compatibility/check?${params}`);
    if (!res.ok) throw new Error(`Failed to fetch compatibility: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function addCompatibilityOverride(data: {
    instructor_id: string;
    student_id: string;
    verdict: string;
    reason?: string;
    initiated_by: string;
}): Promise<CompatibilityOverrideRecord> {
    const res = await apiFetch("/api/compatibility", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to save compatibility override: ${res.statusText}`);
    const body = await res.json();
    return Array.isArray(body.data) ? body.data[0] : body.data;
}

export async function removeCompatibilityOverride(compatibilityId: string): Promise<void> {
    const res = await apiFetch(`/api/compatibility/${compatibilityId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete compatibility override: ${res.statusText}`);
}

export type CompatibleInstructor = {
    instructor_id: string;
    hard_verdict: string | null;
    soft_verdict: string | null;
    reasons: string[];
};

export async function getCompatibleInstructors(studentId: string): Promise<CompatibleInstructor[]> {
    const res = await apiFetch(`/api/compatibility/instructors?student_id=${encodeURIComponent(studentId)}`);
    if (!res.ok) throw new Error(`Failed to fetch compatible instructors: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export type CompatibleStudent = {
    student_id: string;
    hard_verdict: string | null;
    soft_verdict: string | null;
    reasons: string[];
};

export async function getCompatibleStudents(instructorId: string): Promise<CompatibleStudent[]> {
    const res = await apiFetch(`/api/compatibility/students?instructor_id=${encodeURIComponent(instructorId)}`);
    if (!res.ok) throw new Error(`Failed to fetch compatible students: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}