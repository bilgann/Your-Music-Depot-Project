import Button from "@/components/ui/button";
import type { LessonOccurrence } from "@/features/scheduling/api/lesson";

interface Props {
    occurrences: LessonOccurrence[];
    projecting: boolean;
    saving: boolean;
    onProject: () => void;
    onOpenEnroll: (occurrenceId: string) => void;
    onOpenAttendance: (occurrenceId: string, studentId: string, studentName: string, currentStatus: string | null) => void;
    onUnenroll: (occurrenceId: string, studentId: string) => void;
}

function formatDate(value: string) {
    return new Date(value).toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
}

function formatTime(value: string) {
    const normalized = value.includes("T") ? value : `1970-01-01T${value}`;
    return new Date(normalized).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export default function LessonOccurrencesTable({
    occurrences,
    projecting,
    saving,
    onProject,
    onOpenEnroll,
    onOpenAttendance,
    onUnenroll,
}: Props) {
    return (
        <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <p className="table-empty" style={{ margin: 0 }}>
                    Existing projected occurrences are only available after running project in this session because the backend does not expose a lesson-occurrence read endpoint yet.
                </p>
                <Button variant="primary" onClick={onProject} disabled={projecting}>
                    {projecting ? "Projecting..." : "Project Schedule"}
                </Button>
            </div>

            {occurrences.length === 0 ? (
                <p className="table-empty">No projected occurrences yet.</p>
            ) : (
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Status</th>
                                <th>Enrollments</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {occurrences.map((occurrence) => (
                                <tr key={occurrence.occurrence_id}>
                                    <td>{formatDate(occurrence.date)}</td>
                                    <td>{formatTime(occurrence.start_time)} - {formatTime(occurrence.end_time)}</td>
                                    <td>{occurrence.status}</td>
                                    <td>
                                        {occurrence.enrollments?.length ? (
                                            <div style={{ display: "grid", gap: 8 }}>
                                                {occurrence.enrollments.map((enrollment) => (
                                                    <div key={enrollment.enrollment_id} style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                                                        <span>
                                                            {enrollment.student_name}
                                                            {enrollment.attendance_status ? ` (${enrollment.attendance_status})` : ""}
                                                        </span>
                                                        <div style={{ display: "flex", gap: 8 }}>
                                                            <Button
                                                                variant="secondary"
                                                                onClick={() => onOpenAttendance(
                                                                    occurrence.occurrence_id,
                                                                    enrollment.student_id,
                                                                    enrollment.student_name,
                                                                    enrollment.attendance_status
                                                                )}
                                                                disabled={saving}
                                                            >
                                                                Attendance
                                                            </Button>
                                                            <Button
                                                                variant="danger"
                                                                onClick={() => onUnenroll(occurrence.occurrence_id, enrollment.student_id)}
                                                                disabled={saving}
                                                            >
                                                                Remove
                                                            </Button>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        ) : (
                                            "--"
                                        )}
                                    </td>
                                    <td>
                                        <Button variant="primary" onClick={() => onOpenEnroll(occurrence.occurrence_id)} disabled={saving}>
                                            Enroll Student
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}