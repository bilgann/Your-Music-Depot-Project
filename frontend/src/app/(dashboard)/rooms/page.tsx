"use client";

import { useEffect, useState } from "react";
import { apiJson, apiFetch } from "@/lib/api";
import DataState from "@/components/ui/data_state";

type Room = {
    room_id: number;
    name: string;
    capacity: number | null;
};

type FormState = {
    name: string;
    capacity: string;
};

const emptyForm: FormState = { name: "", capacity: "" };

export default function RoomsPage() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Room | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    async function fetchRooms() {
        try {
            setLoading(true);
            const data = await apiJson<Room[]>("/api/rooms");
            setRooms(data);
            setError(null);
        } catch {
            setError("Could not load rooms.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { fetchRooms(); }, []);

    function openAdd() {
        setEditing(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(room: Room) {
        setEditing(room);
        setForm({ name: room.name, capacity: room.capacity?.toString() ?? "" });
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const payload: Record<string, string | number> = { name: form.name };
            if (form.capacity) payload.capacity = parseInt(form.capacity, 10);

            if (editing) {
                await apiFetch(`/api/rooms/${editing.room_id}`, {
                    method: "PUT",
                    body: JSON.stringify(payload),
                });
            } else {
                await apiFetch("/api/rooms", {
                    method: "POST",
                    body: JSON.stringify(payload),
                });
            }
            setShowModal(false);
            await fetchRooms();
        } catch {
            alert("Failed to save room.");
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(id: number) {
        if (!confirm("Delete this room?")) return;
        try {
            await apiFetch(`/api/rooms/${id}`, { method: "DELETE" });
            await fetchRooms();
        } catch {
            alert("Failed to delete room.");
        }
    }

    return (
        <main className="page-rooms">
            <div className="page-header">
                <h1>Rooms</h1>
                <button className="btn btn-primary" onClick={openAdd}>+ Add Room</button>
            </div>

            <DataState loading={loading} error={error} empty={rooms.length === 0} emptyMessage="No rooms found. Add one to get started.">
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Capacity</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rooms.map((room) => (
                                <tr key={room.room_id}>
                                    <td>{room.name}</td>
                                    <td>{room.capacity ?? "--"}</td>
                                    <td>
                                        <div className="actions-cell">
                                            <button className="btn-icon" onClick={() => openEdit(room)} title="Edit">&#9998;</button>
                                            <button className="btn-icon btn-icon--danger" onClick={() => handleDelete(room.room_id)} title="Delete">&#10005;</button>
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
                        <h2>{editing ? "Edit Room" : "Add Room"}</h2>
                        <form onSubmit={handleSubmit}>
                            <div className="form-field">
                                <label>Room Name</label>
                                <input
                                    type="text"
                                    value={form.name}
                                    onChange={(e) => setForm({ ...form, name: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-field">
                                <label>Capacity</label>
                                <input
                                    type="number"
                                    min="1"
                                    value={form.capacity}
                                    onChange={(e) => setForm({ ...form, capacity: e.target.value })}
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
