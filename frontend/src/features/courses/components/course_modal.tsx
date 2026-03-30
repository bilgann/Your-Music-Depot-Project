import Button from "@/components/ui/button";
import Modal from "@/components/ui/modal";
import { NumberField, SelectField, TextField } from "@/components/ui/fields";
import type { CourseInstrument } from "@/features/courses/api/course";
import type { CourseFormState } from "@/features/courses/hooks/use_course_crud";

type Option = { value: string; label: string };

interface Props {
    title: string;
    form: CourseFormState;
    roomOptions: Option[];
    instructorOptions: Option[];
    saving: boolean;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    onChange: (form: CourseFormState) => void;
}

const STATUS_OPTIONS = [
    { value: "draft", label: "Draft" },
    { value: "active", label: "Active" },
    { value: "completed", label: "Completed" },
    { value: "cancelled", label: "Cancelled" },
];

const RATE_OPTIONS = [
    { value: "one_time", label: "One Time" },
    { value: "hourly", label: "Hourly" },
];

const SKILL_OPTIONS = [
    { value: "beginner", label: "Beginner" },
    { value: "elementary", label: "Elementary" },
    { value: "intermediate", label: "Intermediate" },
    { value: "advanced", label: "Advanced" },
    { value: "professional", label: "Professional" },
];

const INSTRUMENT_FAMILY_OPTIONS = [
    { value: "keyboard", label: "Keyboard" },
    { value: "strings", label: "Strings" },
    { value: "woodwind", label: "Woodwind" },
    { value: "brass", label: "Brass" },
    { value: "percussion", label: "Percussion" },
    { value: "voice", label: "Voice" },
    { value: "other", label: "Other" },
];

function toggleInstructorSelection(instructorIds: string[], instructorId: string) {
    return instructorIds.includes(instructorId)
        ? instructorIds.filter((id) => id !== instructorId)
        : [...instructorIds, instructorId];
}

function updateInstrument(instruments: CourseInstrument[], index: number, changes: Partial<CourseInstrument>) {
    return instruments.map((instrument, instrumentIndex) => {
        if (instrumentIndex !== index) return instrument;
        return { ...instrument, ...changes };
    });
}

export default function CourseModal({ title, form, roomOptions, instructorOptions, saving, onClose, onSubmit, onChange }: Props) {
    return (
        <Modal title={title} onClose={onClose} onSubmit={onSubmit} submitLabel={title} saving={saving}>
            <TextField label="Name" value={form.name} onChange={(value) => onChange({ ...form, name: value })} required />
            <TextField label="Description" value={form.description} onChange={(value) => onChange({ ...form, description: value })} />
            <SelectField label="Room" value={form.room_id} onChange={(value) => onChange({ ...form, room_id: value })} options={roomOptions} required />

            <div className="form-field">
                <label>Instructors</label>
                <div style={{ display: "grid", gap: 8 }}>
                    {instructorOptions.map((option, index) => (
                        <label key={option.value} style={{ display: "flex", gap: 8, alignItems: "center" }}>
                            <input
                                type="checkbox"
                                checked={form.instructor_ids.includes(option.value)}
                                onChange={() => onChange({
                                    ...form,
                                    instructor_ids: toggleInstructorSelection(form.instructor_ids, option.value),
                                })}
                            />
                            <span>{option.label}{index === 0 ? "" : ""}</span>
                        </label>
                    ))}
                </div>
                <p className="table-empty" style={{ marginTop: 8 }}>The first selected instructor is treated as the lead instructor.</p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-field">
                    <label>Period Start</label>
                    <input type="date" value={form.period_start} onChange={(e) => onChange({ ...form, period_start: e.target.value })} required />
                </div>
                <div className="form-field">
                    <label>Period End</label>
                    <input type="date" value={form.period_end} onChange={(e) => onChange({ ...form, period_end: e.target.value })} required />
                </div>
            </div>

            <TextField label="Recurrence" value={form.recurrence} onChange={(value) => onChange({ ...form, recurrence: value })} required />

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <div className="form-field">
                    <label>Start Time</label>
                    <input type="time" value={form.start_time} onChange={(e) => onChange({ ...form, start_time: e.target.value })} required />
                </div>
                <div className="form-field">
                    <label>End Time</label>
                    <input type="time" value={form.end_time} onChange={(e) => onChange({ ...form, end_time: e.target.value })} required />
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <SelectField label="Rate Type" value={form.charge_type} onChange={(value) => onChange({ ...form, charge_type: value as "one_time" | "hourly" })} options={RATE_OPTIONS} required />
                <NumberField label="Rate Amount" value={form.rate_amount} onChange={(value) => onChange({ ...form, rate_amount: value })} min={0} step={0.01} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <NumberField label="Capacity" value={form.capacity} onChange={(value) => onChange({ ...form, capacity: value })} min={1} />
                <SelectField label="Status" value={form.status} onChange={(value) => onChange({ ...form, status: value })} options={STATUS_OPTIONS} required />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <SelectField label="Minimum Skill" value={form.skill_min} onChange={(value) => onChange({ ...form, skill_min: value })} options={SKILL_OPTIONS} placeholder="Optional" />
                <SelectField label="Maximum Skill" value={form.skill_max} onChange={(value) => onChange({ ...form, skill_max: value })} options={SKILL_OPTIONS} placeholder="Optional" />
            </div>

            <div className="form-field">
                <label>Required Instruments</label>
                <div style={{ display: "grid", gap: 12 }}>
                    {form.required_instruments.map((instrument, index) => (
                        <div key={`${instrument.name}-${index}`} style={{ display: "grid", gridTemplateColumns: "1fr 1fr auto", gap: 12, alignItems: "end" }}>
                            <TextField
                                label={`Instrument ${index + 1}`}
                                value={instrument.name}
                                onChange={(value) => onChange({
                                    ...form,
                                    required_instruments: updateInstrument(form.required_instruments, index, { name: value }),
                                })}
                            />
                            <SelectField
                                label="Family"
                                value={instrument.family}
                                onChange={(value) => onChange({
                                    ...form,
                                    required_instruments: updateInstrument(form.required_instruments, index, { family: value as CourseInstrument["family"] }),
                                })}
                                options={INSTRUMENT_FAMILY_OPTIONS}
                            />
                            <Button
                                variant="danger"
                                onClick={() => onChange({
                                    ...form,
                                    required_instruments: form.required_instruments.filter((_, instrumentIndex) => instrumentIndex !== index),
                                })}
                            >
                                Remove
                            </Button>
                        </div>
                    ))}
                </div>
                <div style={{ marginTop: 12 }}>
                    <Button
                        variant="secondary"
                        onClick={() => onChange({
                            ...form,
                            required_instruments: [...form.required_instruments, { name: "", family: "other" }],
                        })}
                    >
                        Add Instrument
                    </Button>
                </div>
            </div>
        </Modal>
    );
}