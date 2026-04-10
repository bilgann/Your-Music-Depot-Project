import { useState, useEffect } from "react";
import { getClientById, getClientStudents, getClientInvoices, getClientPayments } from "@/features/clients/api/client";
import type { Client, ClientStudent, ClientInvoice, ClientPayment } from "@/features/clients/api/client";

export function useClientDetail(clientId: string) {
    const [client, setClient] = useState<Client | null>(null);
    const [students, setStudents] = useState<ClientStudent[]>([]);
    const [invoices, setInvoices] = useState<ClientInvoice[]>([]);
    const [payments, setPayments] = useState<ClientPayment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            // Only show skeleton on initial load, not on refreshes
            if (!client) setLoading(true);
            const [clientData, studentsData, invoicesData, paymentsData] = await Promise.all([
                getClientById(clientId),
                getClientStudents(clientId),
                getClientInvoices(clientId),
                getClientPayments(clientId),
            ]);
            setClient(clientData);
            setStudents(studentsData);
            setInvoices(invoicesData);
            setPayments(paymentsData);
            setError(null);
        } catch {
            setError("Could not load client details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, [clientId]);

    return { client, students, invoices, payments, loading, error, refresh };
}
