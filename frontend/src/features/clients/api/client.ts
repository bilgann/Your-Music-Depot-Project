import { apiFetch } from "@/lib/api";

export type Client = {
    client_id: string;
    person: {
        person_id: string;
        name: string;
        email: string | null;
        phone: string | null;
    };
    credits: number;
};

export type ClientStudent = {
    student_id: string;
    person: {
        person_id: string;
        name: string;
        email: string | null;
        phone: string | null;
    };
};

export type ClientInvoice = {
    invoice_id: string;
    period_start: string;
    period_end: string;
    total_amount: number;
    amount_paid: number;
    status: string;
};

export type ClientPayment = {
    payment_id: string;
    amount: number;
    payment_method: string | null;
    paid_on: string | null;
    invoice_id: string;
};

export async function getClients(): Promise<Client[]> {
    const res = await apiFetch("/api/clients");
    if (!res.ok) throw new Error(`Failed to fetch clients: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getClientById(clientId: string): Promise<Client> {
    const res = await apiFetch(`/api/clients/${clientId}`);
    if (!res.ok) throw new Error(`Failed to fetch client: ${res.statusText}`);
    const body = await res.json();
    return Array.isArray(body.data) ? body.data[0] : body.data;
}

export async function getClientStudents(clientId: string): Promise<ClientStudent[]> {
    const res = await apiFetch(`/api/clients/${clientId}/students`);
    if (!res.ok) throw new Error(`Failed to fetch client students: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getClientInvoices(clientId: string): Promise<ClientInvoice[]> {
    const res = await apiFetch(`/api/clients/${clientId}/invoices`);
    if (!res.ok) throw new Error(`Failed to fetch client invoices: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getClientPayments(clientId: string): Promise<ClientPayment[]> {
    const res = await apiFetch(`/api/clients/${clientId}/payments`);
    if (!res.ok) throw new Error(`Failed to fetch client payments: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function createClient(data: { name: string; email?: string; phone?: string }): Promise<Client> {
    const res = await apiFetch("/api/clients", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create client: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function updateClient(clientId: string, data: { name?: string; email?: string; phone?: string }): Promise<Client> {
    const res = await apiFetch(`/api/clients/${clientId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to update client: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function deleteClient(clientId: string): Promise<void> {
    const res = await apiFetch(`/api/clients/${clientId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete client: ${res.statusText}`);
}

export async function recordClientPayment(clientId: string, data: { amount: number; payment_method: string }): Promise<void> {
    const res = await apiFetch(`/api/clients/${clientId}/pay`, {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to record payment: ${res.statusText}`);
}
