import { useState } from "react";
import { createInstructor, updateInstructor, deleteInstructor } from "@/features/instructors/api/instructor";
import type { Instructor } from "@/features/instructors/api/instructor";

type FormState = { name: string; email: string; phone: string };
const emptyForm: FormState = { name: "", email: "", phone: "" };

export function useInstructorCrud(refresh: () => Promise<void>) {
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Instructor | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    function openAdd() {
        setEditing(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(inst: Instructor) {
        setEditing(inst);
        setForm({ name: inst.name, email: inst.email ?? "", phone: inst.phone ?? "" });
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const payload = { name: form.name, ...(form.email && { email: form.email }), ...(form.phone && { phone: form.phone }) };
            if (editing) { await updateInstructor(editing.instructor_id, payload); } else { await createInstructor(payload); }
            setShowModal(false);
            await refresh();
        } catch { alert("Failed to save instructor."); }
        finally { setSaving(false); }
    }

    async function handleDelete(inst: Instructor) {
        if (!confirm("Delete this instructor?")) return;
        try { await deleteInstructor(inst.instructor_id); await refresh(); }
        catch { alert("Failed to delete instructor."); }
    }

    return { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete };
}
