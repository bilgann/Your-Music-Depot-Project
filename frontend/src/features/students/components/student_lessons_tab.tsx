import DataTable from "@/components/ui/data_table";
import type { StudentEnrollment } from "@/features/students/api/student";

interface Props {
    enrollments: StudentEnrollment[];
}

function formatDateTime(iso: string) {
    return new Date(iso).toLocaleString([], {
        weekday: "short", month: "short", day: "numeric",
        hour: "2-digit", minute: "2-digit",
    });
}

const ATTENDANCE_LABELS: Record<string, string> = {
    Present:     "Present",
    Absent:      "Absent",
    Cancelled:   "Cancelled",
    "Late Cancel": "Late Cancel",
    Excused:     "Excused",
};

export default function StudentLessonsTab({ enrollments }: Props) {
    return (
        <DataTable
            loading={false}
            error={null}
            data={enrollments}
            emptyMessage="No lessons enrolled."
            getKey={(e) => e.enrollment_id}
            columns={[
                { header: "Date & Time", render: (e) => formatDateTime(e.lesson.start_time) },
                { header: "Instructor", render: (e) => e.lesson.instructor?.name || "--" },
                { header: "Room", render: (e) => e.lesson.room?.name || "--" },
                { header: "Status", render: (e) => e.lesson.status || "--" },
                {
                    header: "Attendance",
                    render: (e) => e.attendance_status ? (
                        <span className={`status-badge status-${e.attendance_status.toLowerCase().replace(" ", "-")}`}>
                            {ATTENDANCE_LABELS[e.attendance_status] ?? e.attendance_status}
                        </span>
                    ) : "--",
                },
            ]}
        />
    );
}
