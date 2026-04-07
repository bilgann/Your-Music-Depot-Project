import Modal from "@/components/ui/modal";
import { SelectField } from "@/components/ui/fields";

interface Props {
    studentName: string;
    value: string;
    saving: boolean;
    onChange: (value: string) => void;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

const ATTENDANCE_OPTIONS = [
    { value: "Present", label: "Present" },
    { value: "Absent", label: "Absent" },
    { value: "Late Cancel", label: "Late Cancel" },
];

export default function AttendanceModal({ studentName, value, saving, onChange, onClose, onSubmit }: Props) {
    return (
        <Modal title={`Record Attendance: ${studentName}`} onClose={onClose} onSubmit={onSubmit} submitLabel="Save" saving={saving}>
            <SelectField label="Attendance Status" value={value} onChange={onChange} options={ATTENDANCE_OPTIONS} required />
        </Modal>
    );
}