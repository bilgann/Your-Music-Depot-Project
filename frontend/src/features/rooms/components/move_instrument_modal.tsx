import { useState } from "react";
import Modal from "@/components/ui/modal";
import { NumberField, SelectField } from "@/components/ui/fields";
import type { RoomInstrument } from "@/features/rooms/api/room_detail";

interface Props {
    instrument: RoomInstrument;
    roomOptions: { value: string; label: string }[];
    saving: boolean;
    onClose: () => void;
    onSubmit: (targetRoomId: string, quantity: number) => void;
}

export default function MoveInstrumentModal({ instrument, roomOptions, saving, onClose, onSubmit }: Props) {
    const maxQuantity = instrument.quantity ?? 1;
    const [targetRoomId, setTargetRoomId] = useState("");
    const [quantity, setQuantity] = useState("1");

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        const qty = Math.max(1, Math.min(maxQuantity, parseInt(quantity, 10) || 1));
        onSubmit(targetRoomId, qty);
    }

    return (
        <Modal
            title={`Move ${instrument.name}`}
            onClose={onClose}
            onSubmit={handleSubmit}
            submitLabel={saving ? "Moving..." : "Move"}
            saving={saving}
        >
            <p style={{ margin: "0 0 12px", color: "var(--color-text-subtle)", fontSize: "0.9rem" }}>
                Available: {maxQuantity} {instrument.name} ({instrument.family})
            </p>
            <SelectField
                label="Destination Room"
                value={targetRoomId}
                onChange={setTargetRoomId}
                options={roomOptions}
                required
            />
            <NumberField
                label="Quantity to Move"
                value={quantity}
                onChange={setQuantity}
                min={1}
                step={1}
                required
            />
        </Modal>
    );
}
