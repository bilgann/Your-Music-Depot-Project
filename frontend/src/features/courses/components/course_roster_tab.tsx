import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import type { Student } from "@/features/students/api/student";

interface Props {
    students: Student[];
    saving: boolean;
    onOpenEnrollModal: () => void;
    onUnenroll: (studentId: string) => void;
}

export default function CourseRosterTab({ students, saving, onOpenEnrollModal, onUnenroll }: Props) {
    return (
        <>
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
                <Button variant="primary" onClick={onOpenEnrollModal}>Enroll Student</Button>
            </div>
            <DataTable
                loading={false}
                error={null}
                data={students}
                emptyMessage="No students enrolled in this course yet."
                getKey={(student) => student.student_id}
                columns={[
                    { header: "Name", render: (student) => student.person.name },
                    { header: "Email", render: (student) => student.person.email || "--" },
                    { header: "Phone", render: (student) => student.person.phone || "--" },
                ]}
                onDelete={saving ? undefined : (student) => onUnenroll(student.student_id)}
            />
        </>
    );
}