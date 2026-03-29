"use client";

import { useRouter } from "next/navigation";
import Navbar from "@/components/ui/navbar";
import DataTable from "@/components/ui/data_table";
import Modal from "@/components/ui/modal";
import Button from "@/components/ui/button";
import { TextField } from "@/components/ui/fields";
import { Combobox } from "@/components/ui/combobox";
import { useStudents } from "@/features/students/hooks/use_students";
import { useStudentCrud } from "@/features/students/hooks/use_student_crud";
import { searchClients } from "@/features/clients/api/client";

export default function StudentsPage() {
    const router = useRouter();
    const { students, loading, error, refresh, page, setPage, search, setSearch, pageCount } = useStudents();
    const { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete } = useStudentCrud(refresh);

    return (
        <>
            <Navbar
                title="Students"
                className="page-students"
                search={search}
                onSearchChange={setSearch}
                actions={<Button variant="primary" onClick={openAdd}>+ Add Student</Button>}
            />
            <DataTable
                loading={loading} error={error} data={students}
                emptyMessage="No students found. Add one to get started."
                getKey={(s) => s.student_id}
                columns={[
                    { header: "Name",   render: (s) => s.person?.name ?? "--" },
                    { header: "Email",  render: (s) => s.person?.email || "--" },
                    { header: "Phone",  render: (s) => s.person?.phone || "--" },
                    { header: "Client", render: (s) => s.client?.person?.name || "--" },
                ]}
                onEdit={openEdit} onDelete={handleDelete}
                onRowClick={(s) => router.push(`/students/${s.student_id}`)}
                page={page} pageCount={pageCount} onPageChange={setPage}
            />
            {showModal && (
                <Modal title="Student" onClose={() => setShowModal(false)} onSubmit={handleSubmit} submitLabel={editing ? "Update" : "Create"} saving={saving}>
                    <TextField label="Name"  value={form.name}  onChange={(v) => setForm({ ...form, name: v })}  required />
                    <TextField label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} type="email" />
                    <TextField label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
                    <Combobox
                        label="Client"
                        value={form.client_id}
                        valueLabel={form.clientLabel}
                        onChange={(v, lbl) => setForm({ ...form, client_id: v, clientLabel: lbl ?? "" })}
                        fetchOptions={searchClients}
                        required
                    />
                </Modal>
            )}
        </>
    );
}
