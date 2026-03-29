"use client";

import { useEffect, useState } from "react";
import { apiJson, apiFetch } from "@/lib/api";
import DataState from "@/components/ui/data_state";

type Student = {
    student_id: string;
    person_id: string;
    client_id: string | null;
    person: {
        person_id: string;
        name: string;
        email: string | null;
        phone: string | null;
    };
};

type FormState = {
    name: string;
    email: string;
    phone: string;
};

const emptyForm: FormState = { name: "", email: "", phone: "" };

export default function StudentsPage() {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Student | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    async function fetchStudents() {
        try {
            setLoading(true);
            const data = await apiJson<Student[]>("/api/students");
            setStudents(data);
            setError(null);
        } catch {
            setError("Could not load students.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { fetchStudents(); }, []);

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
                await apiFetch(`/api/students/${editing.student_id}`, {
                    method: "PUT",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/students", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });
            }
            setShowModal(false);
            await fetchStudents();
        } catch {
            alert("Failed to save student.");
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(id: string) {
        if (!confirm("Delete this student?")) return;
        try {
            await apiFetch(`/api/students/${id}`, { method: "DELETE" });
            await fetchStudents();
        } catch {
            alert("Failed to delete student.");
        }
    }

    return (
        <main className="page-students">
            <div className="page-header">
                <h1>Students</h1>
                <button className="btn btn-primary" onClick={openAdd}>+ Add Student</button>
            </div>

            <DataState loading={loading} error={error} empty={students.length === 0} emptyMessage="No students found. Add one to get started.">
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
                            {students.map((stu) => (
                                <tr key={stu.student_id}>
                                    <td>{stu.person.name}</td>
                                    <td>{stu.person.email || "--"}</td>
                                    <td>{stu.person.phone || "--"}</td>
                                    <td>
                                        <div className="actions-cell">
                                            <button className="btn-icon" onClick={() => openEdit(stu)} title="Edit">&#9998;</button>
                                            <button className="btn-icon btn-icon--danger" onClick={() => handleDelete(stu.student_id)} title="Delete">&#10005;</button>
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
                        <h2>{editing ? "Edit Student" : "Add Student"}</h2>
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
