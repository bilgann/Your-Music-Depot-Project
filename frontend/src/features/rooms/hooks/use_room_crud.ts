import { useState } from "react";
import { createRoom, updateRoom, deleteRoom } from "@/features/rooms/api/room";
import { useToast } from "@/components/ui/toast";
import type { Room } from "@/features/rooms/api/room";

type FormState = { name: string; capacity: string };
const emptyForm: FormState = { name: "", capacity: "" };

export function useRoomCrud(refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Room | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

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
            const payload = { name: form.name, ...(form.capacity && { capacity: parseInt(form.capacity, 10) }) };
            if (editing) { await updateRoom(editing.room_id, payload); } else { await createRoom(payload); }
            setShowModal(false);
            toast(editing ? "Room updated." : "Room created.", "success");
            await refresh();
        } catch { toast("Failed to save room.", "error"); }
        finally { setSaving(false); }
    }

    async function handleDelete(room: Room) {
        if (!confirm("Delete this room?")) return;
        try { await deleteRoom(room.room_id); toast("Room deleted.", "success"); await refresh(); }
        catch { toast("Failed to delete room.", "error"); }
    }

    return { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete };
}
