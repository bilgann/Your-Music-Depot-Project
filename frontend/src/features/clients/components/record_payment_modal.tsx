import Modal from "@/components/ui/modal";
import { NumberField, SelectField } from "@/components/ui/fields";

interface Props {
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
    amount: string;
    onAmountChange: (v: string) => void;
    method: string;
    onMethodChange: (v: string) => void;
    saving: boolean;
}

const METHOD_OPTIONS = [
    { value: "cash",          label: "Cash" },
    { value: "card",          label: "Card" },
    { value: "bank_transfer", label: "Bank Transfer" },
    { value: "other",         label: "Other" },
];

export default function RecordPaymentModal({ onClose, onSubmit, amount, onAmountChange, method, onMethodChange, saving }: Props) {
    return (
        <Modal title="Record Payment" onClose={onClose} onSubmit={onSubmit} submitLabel="Submit Payment" saving={saving}>
            <NumberField label="Amount ($)"     value={amount} onChange={onAmountChange} min={0.01} step={0.01} required />
            <SelectField label="Payment Method" value={method} onChange={onMethodChange} options={METHOD_OPTIONS} />
        </Modal>
    );
}
