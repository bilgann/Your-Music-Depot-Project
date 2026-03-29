import { useState, useEffect } from "react";
import { getRooms } from "@/features/rooms/api/room";
import type { Room } from "@/features/rooms/api/room";

export function useRooms() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            setRooms(await getRooms());
            setError(null);
        } catch {
            setError("Could not load rooms.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, []);

    return { rooms, loading, error, refresh };
}
