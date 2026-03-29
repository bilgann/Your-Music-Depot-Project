"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiJson, apiFetch } from "@/lib/api";
import DataState from "@/components/ui/data_state";

type Person = {
    person_id: string;
    name: string;
    email: string | null;
    phone: string | null;
};

type Client = {
    client_id: string;
    person: Person;
    credits: number;
};

type Student = {
    student_id: string;
    person: Person;
};

type Invoice = {
    invoice_id: string;
    period_start: string;
    period_end: string;
    total_amount: number;
    amount_paid: number;
    status: string;
};

type Payment = {
    payment_id: string;
    amount: number;
    payment_method: string | null;
    paid_on: string | null;
    invoice_id: string;
};

type Section = "students" | "invoices" | "payments";

export default function ClientDetailPage() {
    const params = useParams();
    const router = useRouter();
    const clientId = params.clientId as string;

    const [client, setClient] = useState<Client | null>(null);
    const [students, setStudents] = useState<Student[]>([]);
    const [invoices, setInvoices] = useState<Invoice[]>([]);
    const [payments, setPayments] = useState<Payment[]>([]);
    const [activeSection, setActiveSection] = useState<Section>("students");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Pay modal
    const [showPayModal, setShowPayModal] = useState(false);
    const [payAmount, setPayAmount] = useState("");
    const [payMethod, setPayMethod] = useState("cash");
    const [paying, setPaying] = useState(false);

    async function fetchAll() {
        try {
            setLoading(true);
            const [clientData, studentsData, invoicesData, paymentsData] = await Promise.all([
                apiJson<Client[]>(`/api/clients/${clientId}`),
                apiJson<Student[]>(`/api/clients/${clientId}/students`),
                apiJson<Invoice[]>(`/api/clients/${clientId}/invoices`),
                apiJson<Payment[]>(`/api/clients/${clientId}/payments`),
            ]);
            setClient(Array.isArray(clientData) ? clientData[0] : clientData);
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

    useEffect(() => { fetchAll(); }, [clientId]);

    async function handlePay(e: React.FormEvent) {
        e.preventDefault();
        setPaying(true);
        try {
            await apiFetch(`/api/clients/${clientId}/pay`, {
                method: "POST",
                body: JSON.stringify({ amount: parseFloat(payAmount), payment_method: payMethod }),
            });
            setShowPayModal(false);
            setPayAmount("");
            await fetchAll();
        } catch {
            alert("Payment failed.");
        } finally {
            setPaying(false);
        }
    }

    return (
        <main className="page-client-detail">
        <DataState loading={loading} error={error} empty={!client} emptyMessage="Client not found.">
            <div className="page-header">
                <div className="client-detail-back">
                    <button className="btn-back" onClick={() => router.push("/clients")}>&#8592; Clients</button>
                    <h1>{client.person.name}</h1>
                </div>
                <button className="btn btn-primary" onClick={() => setShowPayModal(true)}>+ Record Payment</button>
            </div>

            <div className="client-info-card">
                <div className="client-info-row">
                    <span className="client-info-label">Email</span>
                    <span className="client-info-value">{client.person.email || "--"}</span>
                </div>
                <div className="client-info-row">
                    <span className="client-info-label">Phone</span>
                    <span className="client-info-value">{client.person.phone || "--"}</span>
                </div>
                <div className="client-info-row">
                    <span className="client-info-label">Credits</span>
                    <span className="client-info-value client-credits">${Number(client.credits ?? 0).toFixed(2)}</span>
                </div>
            </div>

            <div className="client-tabs">
                {(["students", "invoices", "payments"] as Section[]).map((s) => (
                    <button
                        key={s}
                        className={`client-tab${activeSection === s ? " active" : ""}`}
                        onClick={() => setActiveSection(s)}
                    >
                        {s.charAt(0).toUpperCase() + s.slice(1)}
                    </button>
                ))}
            </div>

            {activeSection === "students" && (
                <div className="data-table-wrapper">
                    {students.length === 0 ? (
                        <p className="table-empty">No students linked to this client.</p>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Email</th>
                                    <th>Phone</th>
                                </tr>
                            </thead>
                            <tbody>
                                {students.map((stu) => (
                                    <tr key={stu.student_id}>
                                        <td>{stu.person.name}</td>
                                        <td>{stu.person.email || "--"}</td>
                                        <td>{stu.person.phone || "--"}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {activeSection === "invoices" && (
                <div className="data-table-wrapper">
                    {invoices.length === 0 ? (
                        <p className="table-empty">No invoices found.</p>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Period</th>
                                    <th>Total</th>
                                    <th>Paid</th>
                                    <th>Balance</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {invoices.map((inv) => (
                                    <tr key={inv.invoice_id}>
                                        <td>{inv.period_start} – {inv.period_end}</td>
                                        <td>${Number(inv.total_amount).toFixed(2)}</td>
                                        <td>${Number(inv.amount_paid).toFixed(2)}</td>
                                        <td>${(Number(inv.total_amount) - Number(inv.amount_paid)).toFixed(2)}</td>
                                        <td>
                                            <span className={`status-badge status-${inv.status.toLowerCase().replace(" ", "-")}`}>
                                                {inv.status}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {activeSection === "payments" && (
                <div className="data-table-wrapper">
                    {payments.length === 0 ? (
                        <p className="table-empty">No payments recorded.</p>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Amount</th>
                                    <th>Method</th>
                                    <th>Invoice</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payments.map((pay) => (
                                    <tr key={pay.payment_id}>
                                        <td>{pay.paid_on?.slice(0, 10) || "--"}</td>
                                        <td>${Number(pay.amount).toFixed(2)}</td>
                                        <td>{pay.payment_method || "--"}</td>
                                        <td>{pay.invoice_id}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {showPayModal && (
                <div className="modal-overlay" onClick={() => setShowPayModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>Record Payment</h2>
                        <form onSubmit={handlePay}>
                            <div className="form-field">
                                <label>Amount ($)</label>
                                <input
                                    type="number"
                                    min="0.01"
                                    step="0.01"
                                    value={payAmount}
                                    onChange={(e) => setPayAmount(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="form-field">
                                <label>Payment Method</label>
                                <select value={payMethod} onChange={(e) => setPayMethod(e.target.value)}>
                                    <option value="cash">Cash</option>
                                    <option value="card">Card</option>
                                    <option value="bank_transfer">Bank Transfer</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div className="modal-buttons">
                                <button type="button" onClick={() => setShowPayModal(false)}>Cancel</button>
                                <button type="submit" disabled={paying}>
                                    {paying ? "Processing..." : "Submit Payment"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </DataState>
        </main>
    );
}
