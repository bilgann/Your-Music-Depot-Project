import Modal from "@/components/ui/modal";
import { SelectField } from "@/components/ui/fields";

type Option = { value: string; label: string };

interface Props {
    selectedStudentId: string;
    studentOptions: Option[];
    saving: boolean;
    onChange: (studentId: string) => void;
    onClose: () => void;
    onSubmit: (e: React.FormEvent) => void;
}

export default function EnrollStudentModal({
    selectedStudentId,
    studentOptions,
    saving,
    onChange,
    onClose,
    onSubmit,
}: Props) {
    return (
        <Modal title="Enroll Student" onClose={onClose} onSubmit={onSubmit} submitLabel="Enroll" saving={saving}>
            <SelectField
                label="Student"
                value={selectedStudentId}
                onChange={onChange}
                options={studentOptions}
                required
                placeholder="Select student"
            />
        </Modal>
    );
}