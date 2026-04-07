"use client";

import { useParams } from "next/navigation";
import Button from "@/components/ui/button";
import DataState from "@/components/ui/data_state";
import Navbar from "@/components/ui/navbar";
import AddChargeModal from "@/features/invoices/components/add_charge_modal";
import InvoiceDetail from "@/features/invoices/components/invoice_detail";
import { useInvoiceActions } from "@/features/invoices/hooks/use_invoice_actions";
import { useInvoiceDetail } from "@/features/invoices/hooks/use_invoice_detail";

export default function InvoiceDetailPage() {
    const { invoiceId } = useParams() as { invoiceId: string };
    const { invoice, lineItems, studentName, loading, error, refresh } = useInvoiceDetail(invoiceId);
    const {
        showChargeModal,
        setShowChargeModal,
        form,
        setForm,
        saving,
        openChargeModal,
        handleAddCharge,
        handleMarkPaid,
        handleCancel,
    } = useInvoiceActions(invoice, refresh);

    return (
        <>
            <Navbar
                className="page-invoice-detail"
                title={invoice?.invoice_id ?? ""}
                back={{ label: "Invoices", href: "/invoices" }}
                actions={invoice && (
                    <>
                        <Button variant="secondary" onClick={openChargeModal}>Add Charge</Button>
                        <Button variant="primary" onClick={() => void handleMarkPaid()} disabled={saving || Number(invoice.total_amount) <= Number(invoice.amount_paid)}>
                            Mark Paid
                        </Button>
                        <Button variant="danger" onClick={() => void handleCancel()} disabled={saving || invoice.status === "Cancelled"}>
                            Cancel
                        </Button>
                    </>
                )}
            />
            <DataState loading={loading} error={error} empty={!invoice} emptyMessage="Invoice not found.">
                {invoice && <InvoiceDetail invoice={invoice} studentName={studentName} lineItems={lineItems} />}
            </DataState>
            {showChargeModal && (
                <AddChargeModal
                    form={form}
                    saving={saving}
                    onChange={setForm}
                    onClose={() => setShowChargeModal(false)}
                    onSubmit={handleAddCharge}
                />
            )}
        </>
    );
}