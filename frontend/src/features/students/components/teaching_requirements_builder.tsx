import Button from "@/components/ui/button";
import { NumberField, SelectField, TextField } from "@/components/ui/fields";
import type { TeachingRequirement } from "@/features/students/api/student";

interface Props {
    value: TeachingRequirement[];
    onChange: (requirements: TeachingRequirement[]) => void;
}

const REQUIREMENT_TYPE_OPTIONS = [
    { value: "credential", label: "Credential" },
    { value: "min_student_age", label: "Minimum Student Age" },
    { value: "max_student_age", label: "Maximum Student Age" },
];

function updateRequirement(items: TeachingRequirement[], index: number, changes: Partial<TeachingRequirement>) {
    return items.map((item, itemIndex) => itemIndex === index ? { ...item, ...changes } : item);
}

export default function TeachingRequirementsBuilder({ value, onChange }: Props) {
    return (
        <div className="form-field">
            <label>Teaching Requirements</label>
            <div style={{ display: "grid", gap: 12 }}>
                {value.length === 0 ? <p className="table-empty">No teaching requirements added.</p> : null}
                {value.map((requirement, index) => {
                    const isAgeRule = requirement.requirement_type === "min_student_age" || requirement.requirement_type === "max_student_age";

                    return (
                        <div
                            key={`${requirement.requirement_type}-${index}`}
                            style={{
                                display: "grid",
                                gap: 12,
                                border: "1px solid var(--border-color, #ddd)",
                                padding: 12,
                                borderRadius: 8,
                            }}
                        >
                            <SelectField
                                label="Requirement Type"
                                value={requirement.requirement_type}
                                onChange={(nextType) => onChange(updateRequirement(value, index, { requirement_type: nextType as TeachingRequirement["requirement_type"], value: "" }))}
                                options={REQUIREMENT_TYPE_OPTIONS}
                            />
                            {isAgeRule ? (
                                <NumberField
                                    label="Value"
                                    value={requirement.value}
                                    onChange={(nextValue) => onChange(updateRequirement(value, index, { value: nextValue }))}
                                    min={0}
                                />
                            ) : (
                                <TextField
                                    label="Value"
                                    value={requirement.value}
                                    onChange={(nextValue) => onChange(updateRequirement(value, index, { value: nextValue }))}
                                />
                            )}
                            <div>
                                <Button variant="danger" onClick={() => onChange(value.filter((_, itemIndex) => itemIndex !== index))}>
                                    Remove Requirement
                                </Button>
                            </div>
                        </div>
                    );
                })}
            </div>
            <div style={{ marginTop: 12 }}>
                <Button
                    variant="secondary"
                    onClick={() => onChange([...value, { requirement_type: "credential", value: "" }])}
                >
                    Add Requirement
                </Button>
            </div>
        </div>
    );
}