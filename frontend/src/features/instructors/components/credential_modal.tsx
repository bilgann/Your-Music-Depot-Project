import Button from "@/components/ui/button";
import Modal from "@/components/ui/modal";
import { SelectField, TextField } from "@/components/ui/fields";
import type { CredentialFormState } from "@/features/instructors/hooks/use_instructor_detail";
import type { InstrumentProficiency } from "@/features/instructors/api/instructor_detail";

interface Props {
    form: CredentialFormState;
    saving: boolean;
    onChange: (form: CredentialFormState) => void;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

const CREDENTIAL_TYPE_OPTIONS = [
    { value: "musical", label: "Musical" },
    { value: "cpr", label: "CPR" },
    { value: "special_ed", label: "Special Ed" },
    { value: "vulnerable_sector", label: "Vulnerable Sector" },
    { value: "first_aid", label: "First Aid" },
    { value: "other", label: "Other" },
];

const SKILL_OPTIONS = [
    { value: "beginner", label: "Beginner" },
    { value: "elementary", label: "Elementary" },
    { value: "intermediate", label: "Intermediate" },
    { value: "advanced", label: "Advanced" },
    { value: "professional", label: "Professional" },
];

const FAMILY_OPTIONS = [
    { value: "keyboard", label: "Keyboard" },
    { value: "strings", label: "Strings" },
    { value: "woodwind", label: "Woodwind" },
    { value: "brass", label: "Brass" },
    { value: "percussion", label: "Percussion" },
    { value: "voice", label: "Voice" },
    { value: "other", label: "Other" },
];

function updateProficiency(items: InstrumentProficiency[], index: number, changes: Partial<InstrumentProficiency>) {
    return items.map((item, itemIndex) => itemIndex === index ? { ...item, ...changes } : item);
}

export default function CredentialModal({ form, saving, onChange, onClose, onSubmit }: Props) {
    return (
        <Modal title="Add Credential" onClose={onClose} onSubmit={onSubmit} submitLabel="Save Credential" saving={saving}>
            <SelectField label="Credential Type" value={form.credential_type} onChange={(value) => onChange({ ...form, credential_type: value })} options={CREDENTIAL_TYPE_OPTIONS} required />
            <TextField label="Issued By" value={form.issued_by} onChange={(value) => onChange({ ...form, issued_by: value })} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-field">
                    <label>Issued Date</label>
                    <input type="date" value={form.issued_date} onChange={(e) => onChange({ ...form, issued_date: e.target.value })} />
                </div>
                <div className="form-field">
                    <label>Valid From</label>
                    <input type="date" value={form.valid_from} onChange={(e) => onChange({ ...form, valid_from: e.target.value })} />
                </div>
            </div>
            <div className="form-field">
                <label>Valid Until</label>
                <input type="date" value={form.valid_until} onChange={(e) => onChange({ ...form, valid_until: e.target.value })} />
            </div>

            <div className="form-field">
                <label>Proficiencies</label>
                <div style={{ display: "grid", gap: 12 }}>
                    {form.proficiencies.map((proficiency, index) => (
                        <div key={index} style={{ display: "grid", gap: 12, border: "1px solid var(--border-color, #ddd)", padding: 12, borderRadius: 8 }}>
                            <TextField
                                label="Instrument"
                                value={proficiency.name}
                                onChange={(value) => onChange({ ...form, proficiencies: updateProficiency(form.proficiencies, index, { name: value }) })}
                            />
                            <SelectField
                                label="Family"
                                value={proficiency.family}
                                onChange={(value) => onChange({ ...form, proficiencies: updateProficiency(form.proficiencies, index, { family: value as InstrumentProficiency["family"] }) })}
                                options={FAMILY_OPTIONS}
                            />
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                                <SelectField
                                    label="Minimum Level"
                                    value={proficiency.min_level}
                                    onChange={(value) => onChange({ ...form, proficiencies: updateProficiency(form.proficiencies, index, { min_level: value }) })}
                                    options={SKILL_OPTIONS}
                                />
                                <SelectField
                                    label="Maximum Level"
                                    value={proficiency.max_level}
                                    onChange={(value) => onChange({ ...form, proficiencies: updateProficiency(form.proficiencies, index, { max_level: value }) })}
                                    options={SKILL_OPTIONS}
                                />
                            </div>
                            <div>
                                <Button
                                    variant="danger"
                                    onClick={() => onChange({ ...form, proficiencies: form.proficiencies.filter((_, itemIndex) => itemIndex !== index) })}
                                >
                                    Remove Proficiency
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
                <div style={{ marginTop: 12 }}>
                    <Button
                        variant="secondary"
                        onClick={() => onChange({
                            ...form,
                            proficiencies: [...form.proficiencies, { name: "", family: "other", min_level: "beginner", max_level: "professional" }],
                        })}
                    >
                        Add Proficiency
                    </Button>
                </div>
            </div>
        </Modal>
    );
}