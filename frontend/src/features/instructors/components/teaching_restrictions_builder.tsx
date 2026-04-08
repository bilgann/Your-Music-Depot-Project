import Button from "@/components/ui/button";
import { NumberField, SelectField } from "@/components/ui/fields";
import type { TeachingRestriction } from "@/features/instructors/api/instructor";

interface Props {
    value: TeachingRestriction[];
    onChange: (restrictions: TeachingRestriction[]) => void;
}

const RESTRICTION_TYPE_OPTIONS = [
    { value: "min_student_age", label: "Minimum Student Age" },
    { value: "max_student_age", label: "Maximum Student Age" },
];

function updateRestriction(items: TeachingRestriction[], index: number, changes: Partial<TeachingRestriction>) {
    return items.map((item, i) => (i === index ? { ...item, ...changes } : item));
}

export default function TeachingRestrictionsBuilder({ value, onChange }: Props) {
    return (
        <div className="form-field">
            <label>Teaching Restrictions</label>
            <div style={{ display: "grid", gap: 12 }}>
                {value.length === 0 ? <p className="table-empty">No teaching restrictions added.</p> : null}
                {value.map((restriction, index) => (
                    <div
                        key={`${restriction.requirement_type}-${index}`}
                        style={{
                            display: "grid",
                            gap: 12,
                            border: "1px solid var(--border-color, #ddd)",
                            padding: 12,
                            borderRadius: 8,
                        }}
                    >
                        <SelectField
                            label="Restriction Type"
                            value={restriction.requirement_type}
                            onChange={(v) =>
                                onChange(updateRestriction(value, index, { requirement_type: v as TeachingRestriction["requirement_type"], value: "" }))
                            }
                            options={RESTRICTION_TYPE_OPTIONS}
                        />
                        <NumberField
                            label="Age"
                            value={restriction.value}
                            onChange={(v) => onChange(updateRestriction(value, index, { value: v }))}
                            min={0}
                        />
                        <div>
                            <Button variant="danger" onClick={() => onChange(value.filter((_, i) => i !== index))}>
                                Remove Restriction
                            </Button>
                        </div>
                    </div>
                ))}
            </div>
            <div style={{ marginTop: 12 }}>
                <Button
                    variant="secondary"
                    onClick={() => onChange([...value, { requirement_type: "min_student_age", value: "" }])}
                >
                    Add Restriction
                </Button>
            </div>
        </div>
    );
}
