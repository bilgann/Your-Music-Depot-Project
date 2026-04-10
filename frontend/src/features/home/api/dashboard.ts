import { apiFetch } from "@/lib/api";
import type { Lesson } from "@/types/index";

export async function getLessons(): Promise<Lesson[]> {
    const res = await apiFetch("/api/lessons");
    if (!res.ok) throw new Error(`Failed to fetch lessons: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}
