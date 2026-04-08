import Modal from "@/components/ui/modal";
import { NumberField, SelectField, TextField } from "@/components/ui/fields";

interface Props {
    form: { item_type: string; description: string; amount: string };
    saving: boolean;
    onChange: (form: { item_type: string; description: string; amount: string }) => void;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

const ITEM_TYPE_OPTIONS = [
    { value: "instrument_damage", label: "Instrument Damage" },
    { value: "instrument_purchase", label: "Instrument Purchase" },
    { value: "other", label: "Other" },
];

export default function AddChargeModal({ form, saving, onChange, onClose, onSubmit }: Props) {
    return (
        <Modal title="Add Charge" onClose={onClose} onSubmit={onSubmit} submitLabel="Add Charge" saving={saving}>
            <SelectField label="Item Type" value={form.item_type} onChange={(value) => onChange({ ...form, item_type: value })} options={ITEM_TYPE_OPTIONS} required />
            <TextField label="Description" value={form.description} onChange={(value) => onChange({ ...form, description: value })} required />
            <NumberField label="Amount" value={form.amount} onChange={(value) => onChange({ ...form, amount: value })} min={0.01} step={0.01} required />
        </Modal>
    );
}