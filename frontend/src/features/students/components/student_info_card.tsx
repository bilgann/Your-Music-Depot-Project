import Link from "next/link";
import InfoCard from "@/components/ui/info_card";
import type { Student } from "@/features/students/api/student";

interface Props {
    student: Student;
}

export default function StudentInfoCard({ student }: Props) {
    const requirementSummary = student.requirements?.length
        ? student.requirements.map((item) => `${item.requirement_type}: ${item.value}`).join(", ")
        : "--";

    return (
        <InfoCard rows={[
            { label: "Email",  value: student.person.email || "--" },
            { label: "Phone",  value: student.person.phone || "--" },
            { label: "Age",    value: student.age ?? "--" },
            { label: "Client", value: student.client_id
                ? <Link href={`/clients/${student.client_id}`} className="link">{student.client?.person?.name ?? student.client_id}</Link>
                : "--" },
            { label: "Requirements", value: requirementSummary },
        ]} />
    );
}
