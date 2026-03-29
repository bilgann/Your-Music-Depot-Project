import Link from "next/link";
import InfoCard from "@/components/ui/info_card";
import type { Student } from "@/features/students/api/student";

interface Props {
    student: Student;
}

export default function StudentInfoCard({ student }: Props) {
    return (
        <InfoCard rows={[
            { label: "Email",  value: student.person.email || "--" },
            { label: "Phone",  value: student.person.phone || "--" },
            { label: "Client", value: student.client_id
                ? <Link href={`/clients/${student.client_id}`} className="link">View Client</Link>
                : "--" },
        ]} />
    );
}
