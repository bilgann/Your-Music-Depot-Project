import { useState } from "react";
import Button from "@/components/ui/button";
import InstrumentSkillLevelBuilder from "./instrument_skill_level_builder";
import type { InstrumentSkillLevel } from "@/features/students/api/student";

interface Props {
    instrumentSkillLevels: InstrumentSkillLevel[];
    saving: boolean;
    onSave: (levels: InstrumentSkillLevel[]) => void;
}

export default function StudentInstrumentsTab({ instrumentSkillLevels, saving, onSave }: Props) {
    const [draft, setDraft] = useState<InstrumentSkillLevel[]>(instrumentSkillLevels);

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <InstrumentSkillLevelBuilder value={draft} onChange={setDraft} />
            <div>
                <Button variant="primary" onClick={() => onSave(draft)} disabled={saving}>
                    {saving ? "Saving..." : "Save Instruments"}
                </Button>
            </div>
        </div>
    );
}
