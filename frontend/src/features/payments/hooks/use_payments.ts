import { useState, useEffect } from "react";
import { getPayments } from "@/features/payments/api/payment";
import type { Payment } from "@/features/payments/api/payment";

export function usePayments() {
    const [payments, setPayments] = useState<Payment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            setPayments(await getPayments());
            setError(null);
        } catch {
            setError("Could not load payments.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, []);

    return { payments, loading, error, refresh };
}
