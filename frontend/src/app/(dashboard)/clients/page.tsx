"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiJson, apiFetch } from "@/lib/api";

type Client = {
    client_id: string;
    person: {
        person_id: string;
        name: string;
        email: string | null;
        phone: string | null;
    };
    credits: number;
};

type FormState = {
    name: string;
    email: string;
    phone: string;
};

const emptyForm: FormState = { name: "", email: "", phone: "" };

export default function ClientsPage() {
    const router = useRouter();
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Client | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    async function fetchClients() {
        try {
            setLoading(true);
            const data = await apiJson<Client[]>("/api/clients");
            setClients(data);
            setError(null);
        } catch {
            setError("Could not load clients.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { fetchClients(); }, []);

    function openAdd() {
        setEditing(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(client: Client) {
        setEditing(client);
        setForm({
            name: client.person.name,
            email: client.person.email ?? "",
            phone: client.person.phone ?? "",
        });
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const payload: Record<string, string> = { name: form.name };
            if (form.email) payload.email = form.email;
            if (form.phone) payload.phone = form.phone;

            if (editing) {
                await apiFetch(`/api/clients/${editing.client_id}`, {
                    method: "PUT",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/clients", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });
            }
            setShowModal(false);
            await fetchClients();
        } catch {
            alert("Failed to save client.");
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(client: Client) {
        if (!confirm(`Delete ${client.person.name}?`)) return;
        try {
            await apiFetch(`/api/clients/${client.client_id}`, { method: "DELETE" });
            await fetchClients();
        } catch {
            alert("Failed to delete client.");
        }
    }

    return (
        <main className="page-clients">
            <div className="page-header">
                <h1>Clients</h1>
                <button className="btn btn-primary" onClick={openAdd}>+ Add Client</button>
            </div>

            {error && <p className="table-error">{error}</p>}

            {loading ? (
                <p className="table-loading">Loading clients...</p>
            ) : clients.length === 0 ? (
                <p className="table-empty">No clients found. Add one to get started.</p>
            ) : (
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Credits</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {clients.map((client) => (
                                <tr
                                    key={client.client_id}
                                    className="client-row"
                                    onClick={() => router.push(`/clients/${client.client_id}`)}
                                >
                                    <td>{client.person.name}</td>
                                    <td>{client.person.email || "--"}</td>
                                    <td>{client.person.phone || "--"}</td>
                                    <td>${Number(client.credits ?? 0).toFixed(2)}</td>
                                    <td>
                                        <div className="actions-cell" onClick={(e) => e.stopPropagation()}>
                                            <button className="btn-icon" onClick={() => openEdit(client)} title="Edit">&#9998;</button>
                                            <button className="btn-icon btn-icon--danger" onClick={() => handleDelete(client)} title="Delete">&#10005;</button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>{editing ? "Edit Client" : "Add Client"}</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-field">
                                <label>Name</label>
                                <input
                                    type="text"
                                    value={form.name}
                                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-field">
                                <label>Email</label>
                                <input
                                    type="email"
                                    value={form.email}
                                    onChange={(e) => setForm({ ...form, email: e.target.value })}
                                />
                            </div>
                            <div className="form-field">
                                <label>Phone</label>
                                <input
                                    type="text"
                                    value={form.phone}
                                    onChange={(e) => setForm({ ...form, phone: e.target.value })}
                                />
                            </div>
                            <div className="modal-buttons">
                                <button type="button" onClick={() => setShowModal(false)}>Cancel</button>
                                <button type="submit" disabled={saving}>
                                    {saving ? "Saving..." : editing ? "Update" : "Create"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </main>
    );
}
