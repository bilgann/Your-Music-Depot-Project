import { useState } from "react";
import { createPayment, deletePayment } from "@/features/payments/api/payment";
import type { Payment } from "@/features/payments/api/payment";
import { useToast } from "@/components/ui/toast";

type FormState = { invoice_id: string; amount: string; payment_method: string; notes: string };
const emptyForm: FormState = { invoice_id: "", amount: "", payment_method: "Card", notes: "" };

export function usePaymentCrud(refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    function openAdd() {
        setForm(emptyForm);
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            await createPayment({
                invoice_id: form.invoice_id,
                amount: parseFloat(form.amount),
                ...(form.payment_method && { payment_method: form.payment_method }),
                ...(form.notes && { notes: form.notes }),
            });
            setShowModal(false);
            setForm(emptyForm);
            toast("Payment recorded.", "success");
            await refresh();
        } catch { toast("Failed to record payment.", "error"); }
        finally { setSaving(false); }
    }

    async function handleDelete(p: Payment) {
        if (!confirm("Delete this payment?")) return;
        try { await deletePayment(p.payment_id); toast("Payment deleted.", "success"); await refresh(); }
        catch { toast("Failed to delete payment.", "error"); }
    }

    return { showModal, setShowModal, form, setForm, saving, openAdd, handleSubmit, handleDelete };
}
