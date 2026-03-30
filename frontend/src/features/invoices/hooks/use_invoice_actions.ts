import { useState } from "react";
import { addLineItem, updateInvoice } from "@/features/invoices/api/invoice";
import { createPayment } from "@/features/payments/api/payment";
import { useToast } from "@/components/ui/toast";
import type { Invoice } from "@/features/invoices/api/invoice";

type AddChargeForm = {
    item_type: string;
    description: string;
    amount: string;
};

const emptyForm: AddChargeForm = {
    item_type: "other",
    description: "",
    amount: "",
};

export function useInvoiceActions(invoice: Invoice | null, refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showChargeModal, setShowChargeModal] = useState(false);
    const [form, setForm] = useState<AddChargeForm>(emptyForm);
    const [saving, setSaving] = useState(false);

    function openChargeModal() {
        setForm(emptyForm);
        setShowChargeModal(true);
    }

    async function handleAddCharge(e: React.FormEvent) {
        e.preventDefault();
        if (!invoice) return;
        setSaving(true);
        try {
            await addLineItem(invoice.invoice_id, {
                item_type: form.item_type,
                description: form.description,
                amount: Number(form.amount),
            });
            setShowChargeModal(false);
            await refresh();
        } catch {
            toast("Failed to add charge.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleMarkPaid() {
        if (!invoice) return;
        const remaining = Math.max(0, Number(invoice.total_amount) - Number(invoice.amount_paid));
        if (remaining <= 0) return;

        try {
            setSaving(true);
            await createPayment({
                invoice_id: invoice.invoice_id,
                amount: remaining,
                payment_method: "Card",
                paid_on: new Date().toISOString().slice(0, 10),
            });
            await refresh();
        } catch {
            toast("Failed to mark invoice paid.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleCancel() {
        if (!invoice) return;
        if (!confirm("Cancel this invoice?")) return;

        try {
            setSaving(true);
            await updateInvoice(invoice.invoice_id, { status: "Cancelled" });
            await refresh();
        } catch {
            toast("Failed to cancel invoice.", "error");
        } finally {
            setSaving(false);
        }
    }

    return {
        showChargeModal,
        setShowChargeModal,
        form,
        setForm,
        saving,
        openChargeModal,
        handleAddCharge,
        handleMarkPaid,
        handleCancel,
    };
}