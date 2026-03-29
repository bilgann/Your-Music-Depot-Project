import { useState } from "react";
import { createStudent } from "@/features/students/api/student";

type FormState = { name: string; email: string; phone: string };
const emptyForm: FormState = { name: "", email: "", phone: "" };

export function useAddClientStudent(clientId: string, refresh: () => Promise<void>) {
    const [showModal, setShowModal] = useState(false);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            await createStudent({
                name: form.name,
                ...(form.email && { email: form.email }),
                ...(form.phone && { phone: form.phone }),
                client_id: clientId,
            });
            setShowModal(false);
            setForm(emptyForm);
            await refresh();
        } catch { alert("Failed to add student."); }
        finally { setSaving(false); }
    }

    return { showModal, setShowModal, form, setForm, saving, handleSubmit };
}
