import DataTable from "@/components/ui/data_table";
import type { Lesson } from "@/types/index";

interface Props {
    lessons: Lesson[];
}

function formatDateTime(value: string) {
    return new Date(value).toLocaleString([], {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

export default function InstructorScheduleTab({ lessons }: Props) {
    return (
        <DataTable
            loading={false}
            error={null}
            data={lessons}
            emptyMessage="No upcoming lessons for this instructor."
            getKey={(lesson) => lesson.lesson_id}
            columns={[
                { header: "Start", render: (lesson) => formatDateTime(lesson.start_time) },
                { header: "End", render: (lesson) => formatDateTime(lesson.end_time) },
                { header: "Room", render: (lesson) => lesson.room_id || "--" },
                { header: "Status", render: (lesson) => lesson.status || "--" },
                { header: "Recurrence", render: (lesson) => lesson.recurrence || "--" },
            ]}
        />
    );
}