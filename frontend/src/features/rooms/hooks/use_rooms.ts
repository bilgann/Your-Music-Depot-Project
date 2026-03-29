import { useState, useEffect, useCallback } from "react";
import { listRooms } from "@/features/rooms/api/room";
import type { Room } from "@/features/rooms/api/room";

const PAGE_SIZE = 20;

export function useRooms() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");
    const [total, setTotal] = useState(0);

    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const { data, total: t } = await listRooms(page, PAGE_SIZE, search || undefined);
            setRooms(data);
            setTotal(t);
            setError(null);
        } catch {
            setError("Could not load rooms.");
        } finally {
            setLoading(false);
        }
    }, [page, search]);

    useEffect(() => { refresh(); }, [refresh]);

    function setSearch(s: string) {
        setSearchRaw(s);
        setPage(1);
    }

    return { rooms, loading, error, refresh, page, setPage, search, setSearch, total, pageCount };
}
