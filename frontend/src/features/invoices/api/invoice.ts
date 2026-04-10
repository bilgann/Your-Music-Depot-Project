import { apiFetch } from "@/lib/api";

export type InvoiceLineItem = {
    line_id: string;
    invoice_id: string;
    lesson_id?: string | null;
    item_type?: string;
    description: string;
    amount: number;
    attendance_status?: string | null;
};

export type Invoice = {
    invoice_id: string;
    client_id: string | null;
    student_id: string | null;
    period_start: string;
    period_end: string;
    total_amount: number;
    amount_paid: number;
    status: string;
    created_at?: string | null;
    client?: {
        client_id: string;
        person?: {
            name?: string;
            email?: string | null;
            phone?: string | null;
        } | null;
    } | null;
};

function unwrapOne<T>(data: T | T[]): T {
    return Array.isArray(data) ? data[0] : data;
}

export async function generateInvoice(data: { student_id: string; year: number; month: number }): Promise<{ invoice: Invoice; line_items: InvoiceLineItem[] }> {
    const res = await apiFetch("/api/invoices/generate", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.message ?? "Failed to generate invoice.");
    }
    const body = await res.json();
    return body.data;
}

export async function listInvoices(): Promise<Invoice[]> {
    const res = await apiFetch("/api/invoices");
    if (!res.ok) throw new Error(`Failed to fetch invoices: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function getInvoiceById(invoiceId: string): Promise<Invoice> {
    const res = await apiFetch(`/api/invoices/${invoiceId}`);
    if (!res.ok) throw new Error(`Failed to fetch invoice: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Invoice>(body.data);
}

export async function getInvoiceLineItems(invoiceId: string): Promise<InvoiceLineItem[]> {
    const res = await apiFetch(`/api/invoices/${invoiceId}/line-items`);
    if (!res.ok) throw new Error(`Failed to fetch invoice line items: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function addLineItem(invoiceId: string, data: {
    item_type: string;
    description: string;
    amount: number;
    lesson_id?: string;
}): Promise<InvoiceLineItem> {
    const res = await apiFetch(`/api/invoices/${invoiceId}/line-items`, {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to add line item: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<InvoiceLineItem>(body.data);
}

export async function updateInvoice(invoiceId: string, data: Partial<Pick<Invoice, "status" | "amount_paid" | "total_amount">>): Promise<Invoice> {
    const res = await apiFetch(`/api/invoices/${invoiceId}`, {
        method: "PUT",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to update invoice: ${res.statusText}`);
    const body = await res.json();
    return unwrapOne<Invoice>(body.data);
}

export async function deleteInvoice(invoiceId: string): Promise<void> {
    const res = await apiFetch(`/api/invoices/${invoiceId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete invoice: ${res.statusText}`);
}
