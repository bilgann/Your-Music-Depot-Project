import DataTable from "@/components/ui/data_table";
import type { RoomSession } from "@/features/rooms/api/room_detail";

interface Props {
    sessions: RoomSession[];
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

export default function RoomSessionsTab({ sessions }: Props) {
    return (
        <>
            <p className="table-empty" style={{ marginBottom: 16 }}>
                Upcoming sessions are derived from lesson templates assigned to this room. Room-specific occurrence data is not exposed by the backend yet.
            </p>
            <DataTable
                loading={false}
                error={null}
                data={sessions}
                emptyMessage="No upcoming sessions for this room."
                getKey={(session) => session.lesson_id}
                columns={[
                    { header: "Date", render: (session) => formatDateTime(session.date) },
                    { header: "Instructor", render: (session) => session.instructor_name },
                    { header: "Students", render: (session) => session.student_names.length ? session.student_names.join(", ") : "--" },
                    { header: "Status", render: (session) => session.status || "--" },
                ]}
            />
        </>
    );
}