/**
 * Lesson API — all calls go through the centralised apiFetch wrapper,
 * which handles Authorization headers and 401 redirects automatically.
 */
import { apiFetch } from "@/lib/api";
import type { Lesson } from "@/types/index";

export async function getLessons(weekStart: string, weekEnd: string): Promise<Lesson[]> {
    const res = await apiFetch(
        `/api/lessons?weekStart=${weekStart}&weekEnd=${weekEnd}`
    );
    if (!res.ok) throw new Error(`Failed to fetch lessons: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
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
