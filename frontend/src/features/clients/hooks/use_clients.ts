import { useState, useEffect } from "react";
import { getClients } from "@/features/clients/api/client";
import type { Client } from "@/features/clients/api/client";

export function useClients() {
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            setClients(await getClients());
            setError(null);
        } catch {
            setError("Could not load clients.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, []);

    return { clients, loading, error, refresh };
}
