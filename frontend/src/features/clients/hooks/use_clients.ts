import { useState, useEffect, useCallback } from "react";
import { listClients } from "@/features/clients/api/client";
import type { Client } from "@/features/clients/api/client";

const PAGE_SIZE = 20;

export function useClients() {
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");
    const [total, setTotal] = useState(0);

    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const { data, total: t } = await listClients(page, PAGE_SIZE, search || undefined);
            setClients(data);
            setTotal(t);
            setError(null);
        } catch {
            setError("Could not load clients.");
        } finally {
            setLoading(false);
        }
    }, [page, search]);

    useEffect(() => { refresh(); }, [refresh]);

    function setSearch(s: string) {
        setSearchRaw(s);
        setPage(1);
    }

    return { clients, loading, error, refresh, page, setPage, search, setSearch, total, pageCount };
}
