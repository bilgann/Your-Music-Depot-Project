import { Combobox } from "@/components/ui/combobox";
import { SelectField, TextField } from "@/components/ui/fields";
import Modal from "@/components/ui/modal";
import type { CompatibilityOverrideFormState } from "@/features/students/hooks/use_student_detail";

interface Props {
    form: CompatibilityOverrideFormState;
    saving: boolean;
    instructorOptions: { value: string; label: string }[];
    onChange: (form: CompatibilityOverrideFormState) => void;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

const VERDICT_OPTIONS = [
    { value: "blocked", label: "Blocked" },
    { value: "disliked", label: "Disliked" },
    { value: "preferred", label: "Preferred" },
    { value: "required", label: "Required" },
];

export default function CompatibilityOverrideModal({ form, saving, instructorOptions, onChange, onClose, onSubmit }: Props) {
    const currentInstructorLabel = instructorOptions.find((item) => item.value === form.instructor_id)?.label ?? "";

    return (
        <Modal title="Save Compatibility Override" onClose={onClose} onSubmit={onSubmit} submitLabel="Save Override" saving={saving}>
            <p className="table-empty" style={{ marginBottom: 16 }}>
                Saving an override will create a new record or update the existing pair override for this student and instructor.
            </p>
            <Combobox
                label="Instructor"
                value={form.instructor_id}
                valueLabel={currentInstructorLabel}
                onChange={(value, label) => onChange({ ...form, instructor_id: value || "", reason: form.reason, verdict: form.verdict })}
                options={instructorOptions}
                required
            />
            <SelectField
                label="Verdict"
                value={form.verdict}
                onChange={(value) => onChange({ ...form, verdict: value })}
                options={VERDICT_OPTIONS}
                required
            />
            <TextField label="Reason" value={form.reason} onChange={(value) => onChange({ ...form, reason: value })} />
        </Modal>
    );
}