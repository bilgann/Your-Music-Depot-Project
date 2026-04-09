import { useState, useMemo } from "react";
import Button from "@/components/ui/button";
import Pagination from "@/components/ui/pagination";
import { useClientPagination } from "@/hooks/use_client_pagination";
import type { LessonOccurrence } from "@/features/scheduling/api/lesson";

const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
];
const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getStatusColor(status: string): string {
    const colors: Record<string, string> = {
        Scheduled: "#C3E4FF",
        Completed: "#C3FFD7",
        Cancelled: "#FFED7A",
    };
    return colors[status] ?? "#C3E4FF";
}

function getTextColor(bg: string): string {
    const map: Record<string, string> = {
        "#C3E4FF": "#0B3A66",
        "#C3FFD7": "#0B6B3B",
        "#FFED7A": "#7A5D00",
    };
    return map[bg] ?? "#000";
}

function toDateStr(d: Date): string {
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
}

function formatDate(value: string) {
    return new Date(value).toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
}

function formatTime(value: string) {
    const normalized = value.includes("T") ? value : `1970-01-01T${value}`;
    return new Date(normalized).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

interface OccurrenceCalendarProps {
    occurrences: LessonOccurrence[];
    onOpenEnroll: (occurrenceId: string) => void;
}

function OccurrenceCalendar({ occurrences, onOpenEnroll }: OccurrenceCalendarProps) {
    const initialCursor = useMemo(() => {
        if (!occurrences.length) {
            const now = new Date();
            return new Date(now.getFullYear(), now.getMonth(), 1);
        }
        const sorted = [...occurrences].sort((a, b) => a.date.localeCompare(b.date));
        const [y, m] = sorted[0].date.split("-").map(Number);
        return new Date(y, m - 1, 1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const [cursor, setCursor] = useState(initialCursor);

    const year = cursor.getFullYear();
    const month = cursor.getMonth();

    const cells = useMemo(() => {
        const first = new Date(year, month, 1);
        const gridStart = new Date(first);
        gridStart.setDate(gridStart.getDate() - gridStart.getDay());
        const result: Date[] = [];
        const cur = new Date(gridStart);
        while (result.length < 35 || cur.getMonth() === month) {
            result.push(new Date(cur));
            cur.setDate(cur.getDate() + 1);
            if (result.length >= 42) break;
        }
        return result;
    }, [year, month]);

    const byDate = useMemo(() => {
        const map: Record<string, LessonOccurrence[]> = {};
        for (const occ of occurrences) {
            if (!map[occ.date]) map[occ.date] = [];
            map[occ.date].push(occ);
        }
        return map;
    }, [occurrences]);

    const todayStr = toDateStr(new Date());

    return (
        <div style={{ marginBottom: 24 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
                <button
                    onClick={() => setCursor(new Date(year, month - 1, 1))}
                    style={{ background: "none", border: "1px solid #ddd", borderRadius: 6, padding: "4px 12px", cursor: "pointer", fontSize: "1rem" }}
                >
                    ‹
                </button>
                <span style={{ fontWeight: 600, minWidth: 160, textAlign: "center", fontSize: "1rem" }}>
                    {MONTH_NAMES[month]} {year}
                </span>
                <button
                    onClick={() => setCursor(new Date(year, month + 1, 1))}
                    style={{ background: "none", border: "1px solid #ddd", borderRadius: 6, padding: "4px 12px", cursor: "pointer", fontSize: "1rem" }}
                >
                    ›
                </button>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2, marginBottom: 4 }}>
                {DAY_NAMES.map((d) => (
                    <div key={d} style={{ textAlign: "center", fontSize: "0.75rem", fontWeight: 600, color: "#888", padding: "4px 0" }}>
                        {d}
                    </div>
                ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 2 }}>
                {cells.map((d, i) => {
                    const dateStr = toDateStr(d);
                    const isCurrentMonth = d.getMonth() === month;
                    const isToday = dateStr === todayStr;
                    const dayOccs = byDate[dateStr] ?? [];

                    return (
                        <div
                            key={i}
                            style={{
                                minHeight: 64,
                                border: "1px solid #eee",
                                borderRadius: 6,
                                padding: "4px 6px",
                                background: isToday ? "#f0f7ff" : isCurrentMonth ? "#fff" : "#fafafa",
                                opacity: isCurrentMonth ? 1 : 0.4,
                            }}
                        >
                            <div style={{
                                fontSize: "0.75rem",
                                fontWeight: isToday ? 700 : 400,
                                color: isToday ? "#2563eb" : "#444",
                                marginBottom: 2,
                            }}>
                                {d.getDate()}
                            </div>
                            {dayOccs.map((occ) => {
                                const bg = getStatusColor(occ.status);
                                const color = getTextColor(bg);
                                return (
                                    <div
                                        key={occ.occurrence_id}
                                        onClick={() => onOpenEnroll(occ.occurrence_id)}
                                        title={`${occ.status} — ${formatTime(occ.start_time)} (click to enroll)`}
                                        style={{
                                            background: bg,
                                            color,
                                            fontSize: "0.7rem",
                                            borderRadius: 4,
                                            padding: "2px 4px",
                                            marginBottom: 2,
                                            cursor: "pointer",
                                            overflow: "hidden",
                                            whiteSpace: "nowrap",
                                            textOverflow: "ellipsis",
                                        }}
                                    >
                                        {formatTime(occ.start_time)}
                                    </div>
                                );
                            })}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

interface Props {
    occurrences: LessonOccurrence[];
    projecting: boolean;
    saving: boolean;
    onProject: () => void;
    onOpenEnroll: (occurrenceId: string) => void;
    onOpenAttendance: (occurrenceId: string, studentId: string, studentName: string, currentStatus: string | null) => void;
    onUnenroll: (occurrenceId: string, studentId: string) => void;
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
    const { page, pageCount, pageData, setPage } = useClientPagination(occurrences);

    if (occurrences.length === 0) {
        return (
            <div style={{ textAlign: "center", padding: "48px 0" }}>
                <p className="table-empty" style={{ marginBottom: 20 }}>
                    No projected occurrences yet. Click &ldquo;Enroll Student&rdquo; to generate the schedule.
                </p>
                <Button variant="primary" onClick={onProject} disabled={projecting}>
                    {projecting ? "Generating..." : "Enroll Student"}
                </Button>
            </div>
        );
    }

    return (
        <div>
            <OccurrenceCalendar occurrences={occurrences} onOpenEnroll={onOpenEnroll} />

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
                        {pageData.map((occurrence) => (
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
            <Pagination page={page} pageCount={pageCount} onPageChange={setPage} />
        </div>
    );
}
