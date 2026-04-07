import { useState } from "react";
import Modal from "@/components/ui/modal";
import { NumberField, SelectField, TextField } from "@/components/ui/fields";
import type { RoomInstrument } from "@/features/rooms/api/room_detail";

interface Props {
    saving: boolean;
    onClose: () => void;
    onSubmit: (instrument: RoomInstrument) => void;
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

export default function AddInstrumentModal({ saving, onClose, onSubmit }: Props) {
    const [name, setName] = useState("");
    const [family, setFamily] = useState<RoomInstrument["family"]>("keyboard");
    const [quantity, setQuantity] = useState("1");

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        const isVoice = family === "voice";
        onSubmit({
            name,
            family,
            quantity: isVoice ? null : Math.max(1, parseInt(quantity, 10) || 1),
        });
    }

    return (
        <Modal title="Add Instrument" onClose={onClose} onSubmit={handleSubmit} submitLabel="Add" saving={saving}>
            <TextField label="Name" value={name} onChange={setName} required />
            <SelectField
                label="Family"
                value={family}
                onChange={(v) => setFamily(v as RoomInstrument["family"])}
                options={FAMILY_OPTIONS}
                required
            />
            {family !== "voice" && (
                <NumberField label="Quantity" value={quantity} onChange={setQuantity} min={1} step={1} required />
            )}
        </Modal>
    );
}
