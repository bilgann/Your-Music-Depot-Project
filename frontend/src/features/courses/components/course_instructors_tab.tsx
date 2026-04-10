import { useState } from "react";
import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import { SelectField } from "@/components/ui/fields";
import type { Instructor } from "@/features/instructors/api/instructor";

type Option = { value: string; label: string };

interface Props {
    instructors: Instructor[];
    availableOptions: Option[];
    saving: boolean;
    onAdd: (instructorId: string) => void;
    onRemove: (instructorId: string) => void;
}

export default function CourseInstructorsTab({ instructors, availableOptions, saving, onAdd, onRemove }: Props) {
    const [selectedInstructorId, setSelectedInstructorId] = useState("");

    function handleAdd() {
        if (!selectedInstructorId) return;
        onAdd(selectedInstructorId);
        setSelectedInstructorId("");
    }

    return (
        <>
            <div style={{ display: "grid", gridTemplateColumns: "1fr auto", gap: 12, alignItems: "end", marginBottom: 16 }}>
                <SelectField
                    label="Add Instructor"
                    value={selectedInstructorId}
                    onChange={setSelectedInstructorId}
                    options={availableOptions}
                    placeholder="Select instructor"
                />
                <Button variant="primary" onClick={handleAdd} disabled={!selectedInstructorId || saving}>Add</Button>
            </div>
            <DataTable
                loading={false}
                error={null}
                data={instructors}
                emptyMessage="No instructors assigned to this course."
                getKey={(instructor) => instructor.instructor_id}
                columns={[
                    { header: "Name", render: (instructor) => instructor.name },
                    { header: "Email", render: (instructor) => instructor.email || "--" },
                    { header: "Phone", render: (instructor) => instructor.phone || "--" },
                ]}
                onDelete={saving ? undefined : (instructor) => onRemove(instructor.instructor_id)}
            />
        </>
    );
}