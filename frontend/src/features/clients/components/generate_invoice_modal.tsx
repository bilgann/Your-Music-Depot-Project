import Modal from "@/components/ui/modal";
import { SelectField, NumberField } from "@/components/ui/fields";
import { Combobox } from "@/components/ui/combobox";
import type { ClientStudent } from "@/features/clients/api/client";

interface Props {
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    form: { student_id: string; year: string; month: string };
    onChange: (form: { student_id: string; year: string; month: string }) => void;
    students: ClientStudent[];
    saving: boolean;
}

const MONTH_OPTIONS = [
    { value: "1",  label: "January" },
    { value: "2",  label: "February" },
    { value: "3",  label: "March" },
    { value: "4",  label: "April" },
    { value: "5",  label: "May" },
    { value: "6",  label: "June" },
    { value: "7",  label: "July" },
    { value: "8",  label: "August" },
    { value: "9",  label: "September" },
    { value: "10", label: "October" },
    { value: "11", label: "November" },
    { value: "12", label: "December" },
];

export default function GenerateInvoiceModal({ onClose, onSubmit, form, onChange, students, saving }: Props) {
    const studentOptions = students.map((s) => ({ value: s.student_id, label: s.person.name }));

    return (
        <Modal title="Invoice" onClose={onClose} onSubmit={onSubmit} submitLabel="Generate" saving={saving}>
            <Combobox label="Student" value={form.student_id} onChange={(v) => onChange({ ...form, student_id: v })} options={studentOptions} required />
            <SelectField label="Month"   value={form.month}      onChange={(v) => onChange({ ...form, month: v })}      options={MONTH_OPTIONS} />
            <NumberField label="Year"    value={form.year}        onChange={(v) => onChange({ ...form, year: v })}       min={2020} />
        </Modal>
    );
}
