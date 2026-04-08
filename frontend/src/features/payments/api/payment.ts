import { apiFetch, apiJsonPaged } from "@/lib/api";

export type Payment = {
    payment_id: string;
    invoice_id: string;
    amount: number;
    payment_method: string | null;
    paid_on: string | null;
    notes: string | null;
};

export async function getPayments(): Promise<Payment[]> {
    const res = await apiFetch("/api/payments");
    if (!res.ok) throw new Error(`Failed to fetch payments: ${res.statusText}`);
    const body = await res.json();
    return body.data ?? [];
}

export async function listPayments(
    page = 1,
    pageSize = 20
): Promise<{ data: Payment[]; total: number }> {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
    return apiJsonPaged<Payment>(`/api/payments?${params}`);
}

export async function createPayment(data: {
    invoice_id: string;
    amount: number;
    payment_method?: string;
    notes?: string;
    paid_on?: string;
}): Promise<Payment> {
    const res = await apiFetch("/api/payments", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Failed to create payment: ${res.statusText}`);
    const body = await res.json();
    return body.data;
}

export async function deletePayment(paymentId: string): Promise<void> {
    const res = await apiFetch(`/api/payments/${paymentId}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete payment: ${res.statusText}`);
}
