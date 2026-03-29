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
    if (enrollments.length === 0) {
        return <p className="table-empty">No lessons enrolled.</p>;
    }
    return (
        <div className="data-table-wrapper">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Date &amp; Time</th>
                        <th>Instructor</th>
                        <th>Room</th>
                        <th>Status</th>
                        <th>Attendance</th>
                    </tr>
                </thead>
                <tbody>
                    {enrollments.map((e) => (
                        <tr key={e.enrollment_id}>
                            <td>{formatDateTime(e.lesson.start_time)}</td>
                            <td>{e.lesson.instructor?.name || "--"}</td>
                            <td>{e.lesson.room?.name || "--"}</td>
                            <td>{e.lesson.status || "--"}</td>
                            <td>
                                {e.attendance_status ? (
                                    <span className={`status-badge status-${e.attendance_status.toLowerCase().replace(" ", "-")}`}>
                                        {ATTENDANCE_LABELS[e.attendance_status] ?? e.attendance_status}
                                    </span>
                                ) : "--"}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
