import InfoCard from "@/components/ui/info_card";
import type { InstructorDetail } from "@/features/instructors/api/instructor_detail";

interface Props {
    instructor: InstructorDetail;
}

function formatRestrictions(instructor: InstructorDetail): string {
    const items = instructor.restrictions ?? [];
    if (items.length === 0) return "--";
    return items
        .map((r) => {
            const label = r.requirement_type === "min_student_age" ? "Min Age" : r.requirement_type === "max_student_age" ? "Max Age" : r.requirement_type;
            return `${label}: ${r.value ?? "--"}`;
        })
        .join(", ");
}

export default function InstructorInfoCard({ instructor }: Props) {
    return (
        <InfoCard
            rows={[
                { label: "Email", value: instructor.email || "--" },
                { label: "Phone", value: instructor.phone || "--" },
                { label: "Hourly Rate", value: instructor.hourly_rate != null ? `$${Number(instructor.hourly_rate).toFixed(2)}` : "--" },
                { label: "Status", value: instructor.status || "--" },
                { label: "Teaching Restrictions", value: formatRestrictions(instructor) },
            ]}
        />
    );
}