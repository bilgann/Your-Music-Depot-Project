"use client";

import Navbar from "@/components/ui/navbar";
import DataTable from "@/components/ui/data_table";
import Modal from "@/components/ui/modal";
import Button from "@/components/ui/button";
import { TextField } from "@/components/ui/fields";
import { useInstructors } from "@/features/instructors/hooks/use_instructors";
import { useInstructorCrud } from "@/features/instructors/hooks/use_instructor_crud";

export default function InstructorsPage() {
    const { instructors, loading, error, refresh, page, setPage, search, setSearch, pageCount } = useInstructors();
    const { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete } = useInstructorCrud(refresh);

    return (
        <>
            <Navbar
                title="Instructors"
                className="page-instructor"
                search={search}
                onSearchChange={setSearch}
                actions={<Button variant="primary" onClick={openAdd}>+ Add Instructor</Button>}
            />
            <DataTable
                loading={loading} error={error} data={instructors}
                emptyMessage="No instructors found. Add one to get started."
                getKey={(inst) => inst.instructor_id}
                columns={[
                    { header: "Name",  render: (inst) => inst.name },
                    { header: "Email", render: (inst) => inst.email || "--" },
                    { header: "Phone", render: (inst) => inst.phone || "--" },
                ]}
                onEdit={openEdit} onDelete={handleDelete}
                page={page} pageCount={pageCount} onPageChange={setPage}
            />
            {showModal && (
                <Modal title={editing ? "Edit Instructor" : "Add Instructor"} onClose={() => setShowModal(false)} onSubmit={handleSubmit} submitLabel={editing ? "Update" : "Create"} saving={saving}>
                    <TextField label="Name"  value={form.name}  onChange={(v) => setForm({ ...form, name: v })}  required />
                    <TextField label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} type="email" />
                    <TextField label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
                </Modal>
            )}
        </>
    );
}
