import Modal from "@/components/ui/modal";
import { SelectField, TextField } from "@/components/ui/fields";
import RecurrencePicker from "@/components/ui/recurrence_picker";
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

const SCHEDULE_MODE_OPTIONS = [
    { value: "none", label: "Specific Date(s)" },
    { value: "recurring", label: "Recurring" },
];

export default function BlockedTimeModal({ form, saving, onChange, onClose, onSubmit }: Props) {
    return (
        <Modal title="Add Blocked Time" onClose={onClose} onSubmit={onSubmit} submitLabel="Save Blocked Time" saving={saving}>
            <TextField label="Label" value={form.label} onChange={(value) => onChange({ ...form, label: value })} required />
            <SelectField label="Type" value={form.block_type} onChange={(value) => onChange({ ...form, block_type: value })} options={BLOCK_TYPE_OPTIONS} required />

            <SelectField
                label="Schedule"
                value={form.recurrence_mode}
                onChange={(value) => onChange({ ...form, recurrence_mode: value as "none" | "recurring" })}
                options={SCHEDULE_MODE_OPTIONS}
            />

            {form.recurrence_mode === "none" && (
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
            )}

            {form.recurrence_mode === "recurring" && (
                <RecurrencePicker
                    value={form.recurrence}
                    onChange={(value) => onChange({ ...form, recurrence: value })}
                    showOneTime={false}
                    required
                />
            )}
        </Modal>
    );
}
