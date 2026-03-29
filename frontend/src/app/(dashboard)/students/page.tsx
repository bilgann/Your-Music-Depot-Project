"use client";

import { useRouter } from "next/navigation";
import DataTable from "@/components/ui/data_table";
import Modal from "@/components/ui/modal";
import { TextField } from "@/components/ui/fields";
import { useStudents } from "@/features/students/hooks/use_students";
import { useStudentCrud } from "@/features/students/hooks/use_student_crud";

export default function StudentsPage() {
    const router = useRouter();
    const { students, loading, error, refresh } = useStudents();
    const { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete } = useStudentCrud(refresh);

    return (
        <main className="page-students">
            <DataTable
                title="Students" addLabel="+ Add Student" onAdd={openAdd}
                loading={loading} error={error} data={students}
                emptyMessage="No students found. Add one to get started."
                getKey={(s) => s.student_id}
                columns={[
                    { header: "Name",  render: (s) => s.person.name },
                    { header: "Email", render: (s) => s.person.email || "--" },
                    { header: "Phone", render: (s) => s.person.phone || "--" },
                ]}
                onEdit={openEdit} onDelete={handleDelete}
                onRowClick={(s) => router.push(`/students/${s.student_id}`)}
            />
            {showModal && (
                <Modal title={editing ? "Edit Student" : "Add Student"} onClose={() => setShowModal(false)} onSubmit={handleSubmit} submitLabel={editing ? "Update" : "Create"} saving={saving}>
                    <TextField label="Name"  value={form.name}  onChange={(v) => setForm({ ...form, name: v })}  required />
                    <TextField label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} type="email" />
                    <TextField label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
                </Modal>
            )}
        </main>
    );
}
