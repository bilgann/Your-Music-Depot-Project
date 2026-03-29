"use client";

import { useEffect, useState } from "react";
import { apiJson, apiFetch } from "@/lib/api";
import DataState from "@/components/ui/data_state";

type Payment = {
    payment_id: number;
    invoice_id: number;
    amount: number;
    payment_method: string | null;
    paid_on: string | null;
    notes: string | null;
};

type FormState = {
    invoice_id: string;
    amount: string;
    payment_method: string;
    notes: string;
};

const emptyForm: FormState = { invoice_id: "", amount: "", payment_method: "Card", notes: "" };

export default function PaymentsPage() {
    const [payments, setPayments] = useState<Payment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    async function fetchPayments() {
        try {
            setLoading(true);
            const data = await apiJson<Payment[]>("/api/payments");
            setPayments(data);
            setError(null);
        } catch {
            setError("Could not load payments.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { fetchPayments(); }, []);

    function openRecord() {
        setForm(emptyForm);
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const payload: Record<string, string | number> = {
                invoice_id: parseInt(form.invoice_id, 10),
                amount: parseFloat(form.amount),
            };
            if (form.payment_method) payload.payment_method = form.payment_method;
            if (form.notes) payload.notes = form.notes;

            await apiFetch("/api/payments", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            setShowModal(false);
            await fetchPayments();
        } catch {
            alert("Failed to record payment.");
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(id: number) {
        if (!confirm("Delete this payment?")) return;
        try {
            await apiFetch(`/api/payments/${id}`, { method: "DELETE" });
            await fetchPayments();
        } catch {
            alert("Failed to delete payment.");
        }
    }

    function formatDate(iso: string | null) {
        if (!iso) return "--";
        return new Date(iso).toLocaleDateString([], { year: "numeric", month: "short", day: "numeric" });
    }

    function formatAmount(n: number) {
        return `$${n.toFixed(2)}`;
    }

    return (
        <main className="page-payments">
            <div className="page-header">
                <h1>Payments</h1>
                <button className="btn btn-primary" onClick={openRecord}>+ Record Payment</button>
            </div>

            <DataState loading={loading} error={error} empty={payments.length === 0} emptyMessage="No payments recorded yet.">
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Invoice</th>
                                <th>Amount</th>
                                <th>Method</th>
                                <th>Paid On</th>
                                <th>Notes</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {payments.map((p) => (
                                <tr key={p.payment_id}>
                                    <td>{p.payment_id}</td>
                                    <td>{p.invoice_id}</td>
                                    <td>{formatAmount(p.amount)}</td>
                                    <td>{p.payment_method || "--"}</td>
                                    <td>{formatDate(p.paid_on)}</td>
                                    <td>{p.notes || "--"}</td>
                                    <td>
                                        <div className="actions-cell">
                                            <button className="btn-icon btn-icon--danger" onClick={() => handleDelete(p.payment_id)} title="Delete">&#10005;</button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </DataState>

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Record Payment</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-field">
                                <label>Invoice ID</label>
                                <input
                                    type="number"
                                    min="1"
                                    value={form.invoice_id}
                                    onChange={(e) => setForm({ ...form, invoice_id: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-field">
                                <label>Amount ($)</label>
                                <input
                                    type="number"
                                    min="0.01"
                                    step="0.01"
                                    value={form.amount}
                                    onChange={(e) => setForm({ ...form, amount: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-field">
                                <label>Payment Method</label>
                                <select
                                    value={form.payment_method}
                                    onChange={(e) => setForm({ ...form, payment_method: e.target.value })}
                                >
                                    <option value="Card">Card</option>
                                    <option value="Cash">Cash</option>
                                    <option value="Bank Transfer">Bank Transfer</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div className="form-field">
                                <label>Notes</label>
                                <input
                                    type="text"
                                    value={form.notes}
                                    onChange={(e) => setForm({ ...form, notes: e.target.value })}
                                />
                            </div>
                            <div className="modal-buttons">
                                <button type="button" onClick={() => setShowModal(false)}>Cancel</button>
                                <button type="submit" disabled={saving}>
                                    {saving ? "Saving..." : "Record Payment"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </main>
    );
}
