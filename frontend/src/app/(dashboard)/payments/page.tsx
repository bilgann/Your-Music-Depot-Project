"use client";

import Navbar from "@/components/ui/navbar";
import DataTable from "@/components/ui/data_table";
import Modal from "@/components/ui/modal";
import Button from "@/components/ui/button";
import { NumberField, SelectField, TextField } from "@/components/ui/fields";
import { usePayments } from "@/features/payments/hooks/use_payments";
import { usePaymentCrud } from "@/features/payments/hooks/use_payment_crud";

const METHOD_OPTIONS = [
    { value: "Card", label: "Card" },
    { value: "Cash", label: "Cash" },
    { value: "Bank Transfer", label: "Bank Transfer" },
    { value: "Other", label: "Other" },
];

function formatDate(iso: string | null) {
    if (!iso) return "--";
    return new Date(iso).toLocaleDateString([], { year: "numeric", month: "short", day: "numeric" });
}

export default function PaymentsPage() {
    const { payments, loading, error, refresh, page, setPage, pageCount } = usePayments();
    const { showModal, setShowModal, form, setForm, saving, openAdd, handleSubmit, handleDelete } = usePaymentCrud(refresh);

    return (
        <>
            <Navbar
                title="Payments"
                className="page-payments"
                actions={<Button variant="primary" onClick={openAdd}>+ Record Payment</Button>}
            />
            <DataTable
                loading={loading} error={error} data={payments}
                emptyMessage="No payments recorded yet."
                getKey={(p) => p.payment_id}
                columns={[
                    { header: "ID",      render: (p) => p.payment_id },
                    { header: "Invoice", render: (p) => p.invoice_id },
                    { header: "Amount",  render: (p) => `$${p.amount.toFixed(2)}` },
                    { header: "Method",  render: (p) => p.payment_method || "--" },
                    { header: "Paid On", render: (p) => formatDate(p.paid_on) },
                    { header: "Notes",   render: (p) => p.notes || "--" },
                ]}
                onDelete={handleDelete}
                page={page} pageCount={pageCount} onPageChange={setPage}
            />
            {showModal && (
                <Modal title="Record Payment" onClose={() => setShowModal(false)} onSubmit={handleSubmit} submitLabel="Record Payment" saving={saving}>
                    <NumberField  label="Invoice ID"     value={form.invoice_id}     onChange={(v) => setForm({ ...form, invoice_id: v })}     min={1} required />
                    <NumberField  label="Amount ($)"     value={form.amount}         onChange={(v) => setForm({ ...form, amount: v })}         min={0.01} step={0.01} required />
                    <SelectField  label="Payment Method" value={form.payment_method} onChange={(v) => setForm({ ...form, payment_method: v })} options={METHOD_OPTIONS} />
                    <TextField    label="Notes"          value={form.notes}          onChange={(v) => setForm({ ...form, notes: v })} />
                </Modal>
            )}
        </>
    );
}
