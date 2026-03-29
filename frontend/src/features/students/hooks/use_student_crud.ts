import { useState } from "react";
import { createStudent, updateStudent, deleteStudent } from "@/features/students/api/student";
import type { Student } from "@/features/students/api/student";

type FormState = { name: string; email: string; phone: string; client_id: string; clientLabel: string };
const emptyForm: FormState = { name: "", email: "", phone: "", client_id: "", clientLabel: "" };

export function useStudentCrud(refresh: () => Promise<void>) {
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Student | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    function openAdd() {
        setEditing(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(stu: Student) {
        setEditing(stu);
        setForm({
            name: stu.person.name,
            email: stu.person.email ?? "",
            phone: stu.person.phone ?? "",
            client_id: stu.client_id ?? "",
            clientLabel: stu.client?.person?.name ?? "",
        });
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const payload = {
                name: form.name,
                ...(form.email && { email: form.email }),
                ...(form.phone && { phone: form.phone }),
                client_id: form.client_id,
            };
            if (editing) { await updateStudent(editing.student_id, payload); } else { await createStudent(payload); }
            setShowModal(false);
            await refresh();
        } catch { alert("Failed to save student."); }
        finally { setSaving(false); }
    }

    async function handleDelete(stu: Student) {
        if (!confirm("Delete this student?")) return;
        try { await deleteStudent(stu.student_id); await refresh(); }
        catch { alert("Failed to delete student."); }
    }

    return { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete };
}
