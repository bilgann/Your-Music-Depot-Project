"use client";

import { useRouter } from "next/navigation";
import Navbar from "@/components/ui/navbar";
import DataTable from "@/components/ui/data_table";
import Modal from "@/components/ui/modal";
import Button from "@/components/ui/button";
import { TextField } from "@/components/ui/fields";
import { useClients } from "@/features/clients/hooks/use_clients";
import { useClientCrud } from "@/features/clients/hooks/use_client_crud";

export default function ClientsPage() {
    const router = useRouter();
    const { clients, loading, error, refresh, page, setPage, search, setSearch, pageCount } = useClients();
    const { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete } = useClientCrud(refresh);

    return (
        <>
            <Navbar
                title="Clients"
                className="page-clients"
                search={search}
                onSearchChange={setSearch}
                actions={<Button variant="primary" onClick={openAdd}>+ Add Client</Button>}
            />
            <DataTable
                loading={loading} error={error} data={clients}
                emptyMessage="No clients found. Add one to get started."
                getKey={(c) => c.client_id}
                columns={[
                    { header: "Name",    render: (c) => c.person?.name ?? "--" },
                    { header: "Email",   render: (c) => c.person?.email || "--" },
                    { header: "Phone",   render: (c) => c.person?.phone || "--" },
                    { header: "Credits", render: (c) => `$${Number(c.credits ?? 0).toFixed(2)}` },
                ]}
                onEdit={openEdit} onDelete={handleDelete}
                onRowClick={(c) => router.push(`/clients/${c.client_id}`)}
                page={page} pageCount={pageCount} onPageChange={setPage}
            />
            {showModal && (
                <Modal title={editing ? "Edit Client" : "Add Client"} onClose={() => setShowModal(false)} onSubmit={handleSubmit} submitLabel={editing ? "Update" : "Create"} saving={saving}>
                    <TextField label="Name"  value={form.name}  onChange={(v) => setForm({ ...form, name: v })}  required />
                    <TextField label="Email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} type="email" />
                    <TextField label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
                </Modal>
            )}
        </>
    );
}
