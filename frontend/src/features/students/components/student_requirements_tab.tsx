import { useState } from "react";
import Button from "@/components/ui/button";
import TeachingRequirementsBuilder from "./teaching_requirements_builder";
import type { TeachingRequirement } from "@/features/students/api/student";

interface Props {
    requirements: TeachingRequirement[];
    saving: boolean;
    onSave: (requirements: TeachingRequirement[]) => void;
}

export default function StudentRequirementsTab({ requirements, saving, onSave }: Props) {
    const [draft, setDraft] = useState<TeachingRequirement[]>(requirements);

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <TeachingRequirementsBuilder value={draft} onChange={setDraft} />
            <div>
                <Button variant="primary" onClick={() => onSave(draft)} disabled={saving}>
                    {saving ? "Saving..." : "Save Requirements"}
                </Button>
            </div>
        </div>
    );
}
