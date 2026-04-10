import { useState } from "react";
import { generateInvoice } from "@/features/invoices/api/invoice";
import { useToast } from "@/components/ui/toast";
import type { ClientStudent } from "@/features/clients/api/client";

type FormState = { student_id: string; year: string; month: string };

function defaultForm(): FormState {
    const now = new Date();
    return { student_id: "", year: String(now.getFullYear()), month: String(now.getMonth() + 1) };
}

export function useGenerateInvoice(students: ClientStudent[], refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [form, setForm] = useState<FormState>(defaultForm);
    const [saving, setSaving] = useState(false);

    function openModal() {
        setForm(defaultForm());
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            await generateInvoice({
                student_id: form.student_id,
                year: parseInt(form.year, 10),
                month: parseInt(form.month, 10),
            });
            setShowModal(false);
            await refresh();
        } catch (err: unknown) {
            toast(err instanceof Error ? err.message : "Failed to generate invoice.", "error");
        }
        finally { setSaving(false); }
    }

    return { showModal, setShowModal, openModal, form, setForm, saving, handleSubmit };
}
