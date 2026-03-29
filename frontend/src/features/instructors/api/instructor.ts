import { apiFetch } from "@/lib/api";

export type Instructor = {
    instructor_id: string;
    name: string;
    email: string | null;
    phone: string | null;
};

export async function getInstructors(): Promise<Instructor[]> {
    const res = await apiFetch("/api/instructors");
    if (!res.ok) throw new Error(`Failed to fetch instructors: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function createInstructor(data: { name: string; email?: string; phone?: string }): Promise<Instructor> {
    const res = await apiFetch("/api/instructors", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create instructor: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function updateInstructor(instructorId: string, data: { name?: string; email?: string; phone?: string }): Promise<Instructor> {
    const res = await apiFetch(`/api/instructors/${instructorId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to update instructor: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function deleteInstructor(instructorId: string): Promise<void> {
    const res = await apiFetch(`/api/instructors/${instructorId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete instructor: ${res.statusText}`);
}
