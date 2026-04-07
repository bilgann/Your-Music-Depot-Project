import Modal from "@/components/ui/modal";
import { TextField } from "@/components/ui/fields";

interface Props {
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    form: { name: string; email: string; phone: string };
    onChange: (form: { name: string; email: string; phone: string }) => void;
    saving: boolean;
}

export default function AddStudentModal({ onClose, onSubmit, form, onChange, saving }: Props) {
    return (
        <Modal title="Student" onClose={onClose} onSubmit={onSubmit} submitLabel="Add Student" saving={saving}>
            <TextField label="Name"  value={form.name}  onChange={(v) => onChange({ ...form, name: v })}  required />
            <TextField label="Email" value={form.email} onChange={(v) => onChange({ ...form, email: v })} type="email" />
            <TextField label="Phone" value={form.phone} onChange={(v) => onChange({ ...form, phone: v })} />
        </Modal>
    );
}
