"use client";

import { useEffect, useState } from "react";
import { apiJson, apiFetch } from "@/lib/api";
import DataState from "@/components/ui/data_state";

type Instructor = {
    instructor_id: number;
    name: string;
    email: string | null;
    phone: string | null;
};

type FormState = {
    name: string;
    email: string;
    phone: string;
};

const emptyForm: FormState = { name: "", email: "", phone: "" };

export default function InstructorsPage() {
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Instructor | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    async function fetchInstructors() {
        try {
            setLoading(true);
            const data = await apiJson<Instructor[]>("/api/instructors");
            setInstructors(data);
            setError(null);
        } catch {
            setError("Could not load instructors.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { fetchInstructors(); }, []);

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
            const payload: Record<string, string> = { name: form.name };
            if (form.email) payload.email = form.email;
            if (form.phone) payload.phone = form.phone;

            if (editing) {
                await apiFetch(`/api/instructors/${editing.instructor_id}`, {
                    method: "PUT",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/instructors", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });
            }
            setShowModal(false);
            await fetchInstructors();
        } catch {
            alert("Failed to save instructor.");
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(id: number) {
        if (!confirm("Delete this instructor?")) return;
        try {
            await apiFetch(`/api/instructors/${id}`, { method: "DELETE" });
            await fetchInstructors();
        } catch {
            alert("Failed to delete instructor.");
        }
    }

    return (
        <main className="page-instructor">
            <div className="page-header">
                <h1>Instructors</h1>
                <button className="btn btn-primary" onClick={openAdd}>+ Add Instructor</button>
            </div>

            <DataState loading={loading} error={error} empty={instructors.length === 0} emptyMessage="No instructors found. Add one to get started.">
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {instructors.map((inst) => (
                                <tr key={inst.instructor_id}>
                                    <td>{inst.name}</td>
                                    <td>{inst.email || "--"}</td>
                                    <td>{inst.phone || "--"}</td>
                                    <td>
                                        <div className="actions-cell">
                                            <button className="btn-icon" onClick={() => openEdit(inst)} title="Edit">&#9998;</button>
                                            <button className="btn-icon btn-icon--danger" onClick={() => handleDelete(inst.instructor_id)} title="Delete">&#10005;</button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </DataState>

            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <h2>{editing ? "Edit Instructor" : "Add Instructor"}</h2>
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
