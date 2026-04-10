"use client";

import { useRouter } from "next/navigation";
import DataTable from "@/components/ui/data_table";
import type { ClientStudent } from "@/features/clients/api/client";

interface Props {
    students: ClientStudent[];
}

export default function ClientStudentsTab({ students }: Props) {
    const router = useRouter();

    return (
        <DataTable
            loading={false}
            error={null}
            data={students}
            emptyMessage="No students linked to this client."
            getKey={(stu) => stu.student_id}
            onRowClick={(stu) => router.push(`/students/${stu.student_id}`)}
            columns={[
                { header: "Name", render: (stu) => stu.person.name },
                { header: "Email", render: (stu) => stu.person.email || "--" },
                { header: "Phone", render: (stu) => stu.person.phone || "--" },
            ]}
        />
    );
}
