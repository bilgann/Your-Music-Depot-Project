import { apiFetch } from "@/lib/api";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { Student } from "@/features/students/api/student";

export type RoomInstrument = {
    name: string;
    family: "keyboard" | "strings" | "woodwind" | "brass" | "percussion" | "voice" | "other";
    quantity?: number | null;
};

export type RoomBlockedTime = {
    label: string;
    block_type: string;
    date?: string | null;
    date_range?: { period_start: string; period_end: string } | null;
    recurrence?: { rule_type: string; value: string } | null;
};

export type RoomDetail = {
    room_id: string;
    name: string;
    capacity: number | null;
    instruments?: RoomInstrument[];
    blocked_times?: RoomBlockedTime[];
};

export type RoomLesson = {
    lesson_id: string;
    instructor_id: string;
    room_id: string;
    start_time: string;
    end_time: string;
    rate?: number | null;
    status?: string | null;
    recurrence?: string | null;
    student_ids?: string[];
};

export type RoomSession = {
    lesson_id: string;
    date: string;
    start_time: string;
    end_time: string;
    instructor_name: string;
    student_names: string[];
    status: string | null;
};

function unwrapOne<T>(data: T | T[]): T {
    return Array.isArray(data) ? data[0] : data;
}

export async function getRoomById(roomId: string): Promise<RoomDetail> {
    const res = await apiFetch(`/api/rooms/${roomId}`);
    if (!res.ok) throw new Error(`Failed to fetch room: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<RoomDetail>(body.data);
}

export async function getRoomLessons(): Promise<RoomLesson[]> {
    const res = await apiFetch("/api/lessons");
    if (!res.ok) throw new Error(`Failed to fetch lessons: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function updateRoomBlockedTimes(roomId: string, blockedTimes: RoomBlockedTime[]): Promise<RoomDetail> {
    const res = await apiFetch(`/api/rooms/${roomId}`, {
        method: "PUT",
        body: JSON.stringify({ blocked_times: blockedTimes }),
    });
    if (!res.ok) throw new Error(`Failed to update room blocked times: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<RoomDetail>(body.data);
}

export async function updateRoomInstruments(roomId: string, instruments: RoomInstrument[]): Promise<RoomDetail> {
    const res = await apiFetch(`/api/rooms/${roomId}`, {
        method: "PUT",
        body: JSON.stringify({ instruments }),
    });
    if (!res.ok) throw new Error(`Failed to update room instruments: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<RoomDetail>(body.data);
}

export function buildRoomSessions(
    lessons: RoomLesson[],
    roomId: string,
    instructors: Instructor[],
    students: Student[]
): RoomSession[] {
    const instructorById = Object.fromEntries(instructors.map((item) => [item.instructor_id, item.name]));
    const studentById = Object.fromEntries(students.map((item) => [item.student_id, item.person.name]));

    return lessons
        .filter((lesson) => lesson.room_id === roomId)
        .sort((left, right) => left.start_time.localeCompare(right.start_time))
        .map((lesson) => ({
            lesson_id: lesson.lesson_id,
            date: lesson.start_time,
            start_time: lesson.start_time,
            end_time: lesson.end_time,
            instructor_name: instructorById[lesson.instructor_id] ?? lesson.instructor_id,
            student_names: (lesson.student_ids ?? []).map((studentId) => studentById[studentId] ?? studentId),
            status: lesson.status ?? null,
        }));
}