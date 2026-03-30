"use client";

import { useRouter } from "next/navigation";
import DataTable from "@/components/ui/data_table";
import type { Student } from "@/features/students/api/student";

interface Props {
    students: Student[];
}

export default function InstructorStudentsTab({ students }: Props) {
    const router = useRouter();

    return (
        <DataTable
            loading={false}
            error={null}
            data={students}
            emptyMessage="No active students found for this instructor."
            getKey={(student) => student.student_id}
            onRowClick={(student) => router.push(`/students/${student.student_id}`)}
            columns={[
                { header: "Name", render: (student) => student.person.name },
                { header: "Email", render: (student) => student.person.email || "--" },
                { header: "Phone", render: (student) => student.person.phone || "--" },
            ]}
        />
    );
}
