import { useState, useEffect, useCallback } from "react";
import { listInstructors } from "@/features/instructors/api/instructor";
import type { Instructor } from "@/features/instructors/api/instructor";

const PAGE_SIZE = 20;

export function useInstructors() {
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");
    const [total, setTotal] = useState(0);

    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const { data, total: t } = await listInstructors(page, PAGE_SIZE, search || undefined);
            setInstructors(data);
            setTotal(t);
            setError(null);
        } catch {
            setError("Could not load instructors.");
        } finally {
            setLoading(false);
        }
    }, [page, search]);

    useEffect(() => { refresh(); }, [refresh]);

    function setSearch(s: string) {
        setSearchRaw(s);
        setPage(1);
    }

    return { instructors, loading, error, refresh, page, setPage, search, setSearch, total, pageCount };
}
