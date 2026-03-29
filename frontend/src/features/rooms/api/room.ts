import { apiFetch } from "@/lib/api";

export type Room = {
    room_id: string;
    name: string;
    capacity: number | null;
};

export async function getRooms(): Promise<Room[]> {
    const res = await apiFetch("/api/rooms");
    if (!res.ok) throw new Error(`Failed to fetch rooms: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function createRoom(data: { name: string; capacity?: number }): Promise<Room> {
    const res = await apiFetch("/api/rooms", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create room: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function updateRoom(roomId: string, data: { name?: string; capacity?: number }): Promise<Room> {
    const res = await apiFetch(`/api/rooms/${roomId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to update room: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function deleteRoom(roomId: string): Promise<void> {
    const res = await apiFetch(`/api/rooms/${roomId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete room: ${res.statusText}`);
}
