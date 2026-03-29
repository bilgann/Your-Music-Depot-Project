import { useState, useEffect, useCallback } from "react";
import { listStudents } from "@/features/students/api/student";
import type { Student } from "@/features/students/api/student";

const PAGE_SIZE = 20;

export function useStudents() {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");
    const [total, setTotal] = useState(0);

    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const { data, total: t } = await listStudents(page, PAGE_SIZE, search || undefined);
            setStudents(data);
            setTotal(t);
            setError(null);
        } catch {
            setError("Could not load students.");
        } finally {
            setLoading(false);
        }
    }, [page, search]);

    useEffect(() => { refresh(); }, [refresh]);

    function setSearch(s: string) {
        setSearchRaw(s);
        setPage(1);
    }

    return { students, loading, error, refresh, page, setPage, search, setSearch, total, pageCount };
}
