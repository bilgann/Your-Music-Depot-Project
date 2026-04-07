import InfoCard from "@/components/ui/info_card";
import type { Course } from "@/features/courses/api/course";

interface Props {
    course: Course;
    roomName: string;
    leadInstructorName: string;
}

function formatDateRange(start: string, end: string) {
    return `${start} to ${end}`;
}

export default function CourseInfoCard({ course, roomName, leadInstructorName }: Props) {
    return (
        <InfoCard
            rows={[
                { label: "Name", value: course.name },
                { label: "Description", value: course.description || "--" },
                { label: "Room", value: roomName || "--" },
                { label: "Lead Instructor", value: leadInstructorName || "--" },
                { label: "Period", value: formatDateRange(course.period_start, course.period_end) },
                { label: "Schedule", value: `${course.start_time} - ${course.end_time}` },
                { label: "Status", value: course.status },
                { label: "Enrolled / Capacity", value: `${course.student_ids.length} / ${course.capacity ?? "--"}` },
            ]}
        />
    );
}