import { apiFetch } from "@/lib/api";

export async function generateInvoice(data: { student_id: string; year: number; month: number }): Promise<void> {
    const res = await apiFetch("/api/invoices/generate", {
        method: "POST",
        body: JSON.stringify(data),
    });
    if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.message ?? "Failed to generate invoice.");
    }
}
