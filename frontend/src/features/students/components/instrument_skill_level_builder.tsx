import Button from "@/components/ui/button";
import { SelectField, TextField } from "@/components/ui/fields";
import type { InstrumentSkillLevel } from "@/features/students/api/student";

interface Props {
    value: InstrumentSkillLevel[];
    onChange: (levels: InstrumentSkillLevel[]) => void;
}

const FAMILY_OPTIONS = [
    { value: "keyboard", label: "Keyboard" },
    { value: "strings", label: "Strings" },
    { value: "woodwind", label: "Woodwind" },
    { value: "brass", label: "Brass" },
    { value: "percussion", label: "Percussion" },
    { value: "voice", label: "Voice" },
    { value: "other", label: "Other" },
];

const SKILL_LEVEL_OPTIONS = [
    { value: "beginner", label: "Beginner" },
    { value: "elementary", label: "Elementary" },
    { value: "intermediate", label: "Intermediate" },
    { value: "advanced", label: "Advanced" },
    { value: "professional", label: "Professional" },
];

function update(items: InstrumentSkillLevel[], index: number, changes: Partial<InstrumentSkillLevel>) {
    return items.map((item, i) => (i === index ? { ...item, ...changes } : item));
}

export default function InstrumentSkillLevelBuilder({ value, onChange }: Props) {
    return (
        <div className="form-field">
            <label>Instrument Skill Levels</label>
            <div style={{ display: "grid", gap: 12 }}>
                {value.length === 0 ? (
                    <p className="table-empty">No instruments added.</p>
                ) : null}
                {value.map((isl, index) => (
                    <div
                        key={`${isl.name}-${isl.family}-${index}`}
                        style={{
                            display: "grid",
                            gap: 12,
                            border: "1px solid var(--border-color, #ddd)",
                            padding: 12,
                            borderRadius: 8,
                        }}
                    >
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                            <TextField
                                label="Instrument"
                                value={isl.name}
                                onChange={(v) => onChange(update(value, index, { name: v }))}
                                required
                            />
                            <SelectField
                                label="Family"
                                value={isl.family}
                                onChange={(v) => onChange(update(value, index, { family: v }))}
                                options={FAMILY_OPTIONS}
                                required
                            />
                        </div>
                        <SelectField
                            label="Skill Level"
                            value={isl.skill_level}
                            onChange={(v) => onChange(update(value, index, { skill_level: v }))}
                            options={SKILL_LEVEL_OPTIONS}
                            required
                        />
                        <div>
                            <Button
                                variant="danger"
                                onClick={() => onChange(value.filter((_, i) => i !== index))}
                            >
                                Remove
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
            <div style={{ marginTop: 12 }}>
                <Button
                    variant="secondary"
                    onClick={() =>
                        onChange([...value, { name: "", family: "", skill_level: "beginner" }])
                    }
                >
                    Add Instrument
                </Button>
            </div>
        </div>
    );
}
