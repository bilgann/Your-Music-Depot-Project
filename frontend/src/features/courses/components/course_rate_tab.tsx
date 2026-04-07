import InfoCard from "@/components/ui/info_card";
import type { Course } from "@/features/courses/api/course";

interface Props {
    course: Course;
}

export default function CourseRateTab({ course }: Props) {
    return (
        <InfoCard
            rows={[
                { label: "Charge Type", value: course.rate?.charge_type ?? "--" },
                { label: "Amount", value: course.rate ? `$${course.rate.amount.toFixed(2)}` : "--" },
                { label: "Currency", value: course.rate?.currency ?? "CAD" },
            ]}
        />
    );
}