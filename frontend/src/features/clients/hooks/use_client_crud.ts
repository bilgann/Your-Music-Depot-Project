import { useState } from "react";
import { createClient, updateClient, deleteClient } from "@/features/clients/api/client";
import { useToast } from "@/components/ui/toast";
import type { Client } from "@/features/clients/api/client";

type FormState = { name: string; email: string; phone: string };
const emptyForm: FormState = { name: "", email: "", phone: "" };

export function useClientCrud(refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Client | null>(null);
    const [form, setForm] = useState<FormState>(emptyForm);
    const [saving, setSaving] = useState(false);

    function openAdd() {
        setEditing(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(client: Client) {
        setEditing(client);
        setForm({ name: client.person.name, email: client.person.email ?? "", phone: client.person.phone ?? "" });
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSaving(true);
        try {
            const payload = { name: form.name, ...(form.email && { email: form.email }), ...(form.phone && { phone: form.phone }) };
            if (editing) { await updateClient(editing.client_id, payload); } else { await createClient(payload); }
            setShowModal(false);
            toast(editing ? "Client updated." : "Client created.", "success");
            await refresh();
        } catch { toast("Failed to save client.", "error"); }
        finally { setSaving(false); }
    }

    async function handleDelete(client: Client) {
        if (!confirm(`Delete ${client.person.name}?`)) return;
        try { await deleteClient(client.client_id); toast("Client deleted.", "success"); await refresh(); }
        catch { toast("Failed to delete client.", "error"); }
    }

    return { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete };
}
