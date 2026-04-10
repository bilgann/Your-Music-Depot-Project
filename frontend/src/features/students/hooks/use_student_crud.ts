import { useState } from "react";
import { createStudent, updateStudent, deleteStudent } from "@/features/students/api/student";
import type { Student, TeachingRequirement, InstrumentSkillLevel } from "@/features/students/api/student";
import { useToast } from "@/components/ui/toast";

export type StudentFormState = {
    name: string;
    email: string;
    phone: string;
    client_id: string;
    clientLabel: string;
    age: string;
    instrument_skill_levels: InstrumentSkillLevel[];
    requirements: TeachingRequirement[];
};

const emptyForm: StudentFormState = {
    name: "",
    email: "",
    phone: "",
    client_id: "",
    clientLabel: "",
    age: "",
    instrument_skill_levels: [],
    requirements: [],
};

function sanitizeRequirements(requirements: TeachingRequirement[]) {
    return requirements
        .map((item) => ({
            requirement_type: item.requirement_type,
            value: item.value.trim(),
        }))
        .filter((item) => item.value.length > 0);
}

export function useStudentCrud(refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Student | null>(null);
    const [form, setForm] = useState<StudentFormState>(emptyForm);
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
            age: stu.age != null ? String(stu.age) : "",
            instrument_skill_levels: stu.instrument_skill_levels ?? [],
            requirements: stu.requirements ?? [],
        });
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const requirements = sanitizeRequirements(form.requirements);
            const skillLevels = form.instrument_skill_levels.filter(
                (isl) => isl.name.trim() && isl.family && isl.skill_level,
            );
            const payload = {
                name: form.name,
                ...(form.email && { email: form.email }),
                ...(form.phone && { phone: form.phone }),
                client_id: form.client_id,
                ...(form.age && { age: Number(form.age) }),
                instrument_skill_levels: skillLevels,
                ...(requirements.length > 0 && { requirements }),
            };
            if (editing) { await updateStudent(editing.student_id, payload); } else { await createStudent(payload); }
            setShowModal(false);
            toast(editing ? "Student updated." : "Student created.", "success");
            await refresh();
        } catch { toast("Failed to save student.", "error"); }
        finally { setSaving(false); }
    }

    async function handleDelete(stu: Student) {
        if (!confirm("Delete this student?")) return;
        try { await deleteStudent(stu.student_id); toast("Student deleted.", "success"); await refresh(); }
        catch { toast("Failed to delete student.", "error"); }
    }

    return { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete };
}
