import Modal from "@/components/ui/modal";
import { SelectField, TextField } from "@/components/ui/fields";
import type { BlockedTimeFormState } from "@/features/rooms/hooks/use_room_detail";

interface Props {
    form: BlockedTimeFormState;
    saving: boolean;
    onChange: (form: BlockedTimeFormState) => void;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

const BLOCK_TYPE_OPTIONS = [
    { value: "holiday", label: "Holiday" },
    { value: "weekend", label: "Weekend" },
    { value: "work", label: "Work" },
    { value: "school", label: "School" },
    { value: "vacation", label: "Vacation" },
    { value: "personal", label: "Personal" },
    { value: "other", label: "Other" },
];

export default function BlockedTimeModal({ form, saving, onChange, onClose, onSubmit }: Props) {
    return (
        <Modal title="Add Blocked Time" onClose={onClose} onSubmit={onSubmit} submitLabel="Save Blocked Time" saving={saving}>
            <TextField label="Label" value={form.label} onChange={(value) => onChange({ ...form, label: value })} required />
            <SelectField label="Type" value={form.block_type} onChange={(value) => onChange({ ...form, block_type: value })} options={BLOCK_TYPE_OPTIONS} required />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-field">
                    <label>Start Date</label>
                    <input type="date" value={form.start_date} onChange={(e) => onChange({ ...form, start_date: e.target.value })} required />
                </div>
                <div className="form-field">
                    <label>End Date</label>
                    <input type="date" value={form.end_date} onChange={(e) => onChange({ ...form, end_date: e.target.value })} required />
                </div>
            </div>
        </Modal>
    );
}