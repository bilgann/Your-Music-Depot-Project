import { useState } from "react";
import { createInstructor, updateInstructor, deleteInstructor } from "@/features/instructors/api/instructor";
import type { Instructor, TeachingRestriction } from "@/features/instructors/api/instructor";
import { useToast } from "@/components/ui/toast";

export type InstructorFormState = { name: string; email: string; phone: string; restrictions: TeachingRestriction[] };
const emptyForm: InstructorFormState = { name: "", email: "", phone: "", restrictions: [] };

function toInstructorForm(inst?: Instructor | null): InstructorFormState {
    if (!inst) return emptyForm;

    return {
        name: typeof inst.name === "string" ? inst.name : "",
        email: typeof inst.email === "string" ? inst.email : "",
        phone: typeof inst.phone === "string" ? inst.phone : "",
        restrictions: (inst.restrictions ?? []).map((restriction) => ({
            requirement_type: restriction.requirement_type,
            value: typeof restriction.value === "string" ? restriction.value : String(restriction.value ?? ""),
        })),
    };
}

export function useInstructorCrud(refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Instructor | null>(null);
    const [form, setForm] = useState<InstructorFormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    function openAdd() {
        setEditing(null);
        setForm(toInstructorForm());
        setShowModal(true);
    }

    function openEdit(inst: Instructor) {
        setEditing(inst);
        setForm(toInstructorForm(inst));
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const cleanRestrictions = form.restrictions.filter((r) => r.value !== "");
            const payload = {
                name: form.name,
                ...(form.email && { email: form.email }),
                ...(form.phone && { phone: form.phone }),
                ...(cleanRestrictions.length > 0 && { restrictions: cleanRestrictions }),
            };
            if (editing) { await updateInstructor(editing.instructor_id, payload); } else { await createInstructor(payload); }
            setShowModal(false);
            toast(editing ? "Instructor updated." : "Instructor created.", "success");
            await refresh();
        } catch { toast("Failed to save instructor.", "error"); }
        finally { setSaving(false); }
    }

    async function handleDelete(inst: Instructor) {
        if (!confirm("Delete this instructor?")) return;
        try { await deleteInstructor(inst.instructor_id); toast("Instructor deleted.", "success"); await refresh(); }
        catch { toast("Failed to delete instructor.", "error"); }
    }

    return { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete };
}
