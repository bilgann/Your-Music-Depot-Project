import { useState, useEffect, useCallback, useMemo } from "react";
import { listPayments } from "@/features/payments/api/payment";
import type { Payment } from "@/features/payments/api/payment";

const PAGE_SIZE = 20;

export function usePayments() {
    const [payments, setPayments] = useState<Payment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");
    const [total, setTotal] = useState(0);

    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const { data, total: t } = await listPayments(page, PAGE_SIZE);
            setPayments(data);
            setTotal(t);
            setError(null);
        } catch {
            setError("Could not load payments.");
        } finally {
            setLoading(false);
        }
    }, [page]);

    useEffect(() => { refresh(); }, [refresh]);

    function setSearch(s: string) {
        setSearchRaw(s);
        setPage(1);
    }

    const filtered = useMemo(() => {
        if (!search) return payments;
        const q = search.toLowerCase();
        return payments.filter(
            (p) =>
                p.invoice_id?.toLowerCase().includes(q) ||
                p.payment_method?.toLowerCase().includes(q) ||
                p.notes?.toLowerCase().includes(q)
        );
    }, [payments, search]);

    return { payments: filtered, loading, error, refresh, page, setPage, search, setSearch, total, pageCount };
}
