"use client";

import { useEffect, useState, useMemo } from "react";
import { faChevronLeft, faChevronRight, faPrint } from "@fortawesome/free-solid-svg-icons";
import Button from "@/components/ui/button";
import { getStudentTimetable } from "@/features/students/api/student";
import type { StudentEnrollment } from "@/features/students/api/student";

type ViewMode = "week" | "month";

const WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const WEEKDAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 11 }, (_, i) => 8 + i); // 8 AM - 6 PM

function startOfWeek(d: Date): Date {
    const date = new Date(d);
    const day = date.getDay();
    const diff = (day === 0 ? -6 : 1) - day;
    date.setDate(date.getDate() + diff);
    date.setHours(0, 0, 0, 0);
    return date;
}

function formatDate(d: Date): string {
    return d.toISOString().slice(0, 10);
}

function formatDateReadable(d: Date): string {
    return d.toLocaleDateString(undefined, { month: "long", day: "numeric", year: "numeric" });
}

function addDays(d: Date, n: number): Date {
    const r = new Date(d);
    r.setDate(r.getDate() + n);
    return r;
}

function parseTime(iso: string): { hour: number; minute: number } | null {
    const m = iso.match(/T?(\d{2}):(\d{2})/);
    if (!m) return null;
    return { hour: Number(m[1]), minute: Number(m[2]) };
}

function formatTimeShort(iso: string): string {
    const t = parseTime(iso);
    if (!t) return "";
    const h = t.hour % 12 || 12;
    const ampm = t.hour < 12 ? "AM" : "PM";
    return t.minute ? `${h}:${String(t.minute).padStart(2, "0")} ${ampm}` : `${h} ${ampm}`;
}

interface Props {
    studentId: string;
    studentName: string;
    onClose: () => void;
}

export default function PrintTimetableModal({ studentId, studentName, onClose }: Props) {
    const [view, setView] = useState<ViewMode>("week");
    const [cursor, setCursor] = useState(() => startOfWeek(new Date()));
    const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
    const [loading, setLoading] = useState(false);

    const { rangeStart, rangeEnd, rangeLabel } = useMemo(() => {
        if (view === "week") {
            const start = cursor;
            const end = addDays(cursor, 4); // Mon-Fri
            return {
                rangeStart: formatDate(start),
                rangeEnd: formatDate(addDays(cursor, 6)),
                rangeLabel: `${formatDateReadable(start)} - ${formatDateReadable(end)}`,
            };
        }
        const start = new Date(cursor.getFullYear(), cursor.getMonth(), 1);
        const end = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0);
        return {
            rangeStart: formatDate(start),
            rangeEnd: formatDate(end),
            rangeLabel: start.toLocaleDateString(undefined, { month: "long", year: "numeric" }),
        };
    }, [view, cursor]);

    useEffect(() => {
        setLoading(true);
        getStudentTimetable(studentId, rangeStart, rangeEnd)
            .then(setEnrollments)
            .catch(() => setEnrollments([]))
            .finally(() => setLoading(false));
    }, [studentId, rangeStart, rangeEnd]);

    function prev() {
        if (view === "week") setCursor(addDays(cursor, -7));
        else setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1));
    }

    function next() {
        if (view === "week") setCursor(addDays(cursor, 7));
        else setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1));
    }

    function switchView(v: ViewMode) {
        setView(v);
        if (v === "week") setCursor(startOfWeek(new Date()));
        else setCursor(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
    }

    // Group enrollments by date string
    const byDate = useMemo(() => {
        const map: Record<string, StudentEnrollment[]> = {};
        for (const e of enrollments) {
            const dateStr = e.lesson.start_time.slice(0, 10);
            if (!map[dateStr]) map[dateStr] = [];
            map[dateStr].push(e);
        }
        return map;
    }, [enrollments]);

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="timetable-modal" onClick={(e) => e.stopPropagation()}>
                {/* Controls - hidden during print */}
                <div className="timetable-controls no-print">
                    <div className="timetable-controls__left">
                        <Button variant="icon" icon={faChevronLeft} onClick={prev} title="Previous" />
                        <Button variant="icon" icon={faChevronRight} onClick={next} title="Next" />
                        <div className="timetable-view-tabs">
                            {(["week", "month"] as ViewMode[]).map((v) => (
                                <button
                                    key={v}
                                    type="button"
                                    className={`timetable-view-tab${view === v ? " active" : ""}`}
                                    onClick={() => switchView(v)}
                                >
                                    {v === "week" ? "Weekly" : "Monthly"}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="timetable-controls__right">
                        <Button variant="primary" icon={faPrint} onClick={() => window.print()}>Print</Button>
                        <Button variant="secondary" onClick={onClose}>Close</Button>
                    </div>
                </div>

                {/* Printable timetable */}
                <div className="print-timetable">
                    <div className="print-timetable__header">
                        <h2>{studentName}</h2>
                        <p>{view === "week" ? "Weekly" : "Monthly"} Timetable &mdash; {rangeLabel}</p>
                    </div>

                    {loading ? (
                        <p className="print-timetable__loading">Loading...</p>
                    ) : view === "week" ? (
                        <WeekView cursor={cursor} byDate={byDate} />
                    ) : (
                        <MonthView cursor={cursor} byDate={byDate} />
                    )}
                </div>
            </div>
        </div>
    );
}

function WeekView({ cursor, byDate }: { cursor: Date; byDate: Record<string, StudentEnrollment[]> }) {
    const days = WEEKDAY_NAMES.map((_, i) => addDays(cursor, i));

    return (
        <table className="print-timetable__week">
            <thead>
                <tr>
                    <th className="print-timetable__time-col">Time</th>
                    {days.map((d, i) => (
                        <th key={i}>
                            {WEEKDAY_NAMES[i]}
                            <br />
                            <span className="print-timetable__date-num">{d.getDate()}</span>
                        </th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {HOURS.map((h) => (
                    <tr key={h}>
                        <td className="print-timetable__time-cell">
                            {h < 12 ? `${h} AM` : h === 12 ? "12 PM" : `${h - 12} PM`}
                        </td>
                        {days.map((d, di) => {
                            const dateStr = formatDate(d);
                            const lessons = (byDate[dateStr] || []).filter((e) => {
                                const t = parseTime(e.lesson.start_time);
                                return t && t.hour === h;
                            });
                            return (
                                <td key={di} className="print-timetable__cell">
                                    {lessons.map((e) => (
                                        <div key={e.enrollment_id} className="print-timetable__lesson">
                                            <span className="print-timetable__lesson-time">
                                                {formatTimeShort(e.lesson.start_time)} - {formatTimeShort(e.lesson.end_time)}
                                            </span>
                                            {e.lesson.instructor?.name && (
                                                <span className="print-timetable__lesson-detail">{e.lesson.instructor.name}</span>
                                            )}
                                            {e.lesson.room?.name && (
                                                <span className="print-timetable__lesson-detail">{e.lesson.room.name}</span>
                                            )}
                                        </div>
                                    ))}
                                </td>
                            );
                        })}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

function MonthView({ cursor, byDate }: { cursor: Date; byDate: Record<string, StudentEnrollment[]> }) {
    const year = cursor.getFullYear();
    const month = cursor.getMonth();
    const firstDay = new Date(year, month, 1);
    const gridStart = new Date(firstDay);
    gridStart.setDate(gridStart.getDate() - gridStart.getDay());

    const cells: Date[] = [];
    const cur = new Date(gridStart);
    while (cells.length < 42) {
        cells.push(new Date(cur));
        cur.setDate(cur.getDate() + 1);
        if (cells.length >= 35 && cur.getMonth() !== month) break;
    }

    return (
        <table className="print-timetable__month">
            <thead>
                <tr>
                    {WEEKDAY_SHORT.map((name) => (
                        <th key={name}>{name}</th>
                    ))}
                </tr>
            </thead>
            <tbody>
                {Array.from({ length: Math.ceil(cells.length / 7) }, (_, week) => (
                    <tr key={week}>
                        {cells.slice(week * 7, week * 7 + 7).map((d, di) => {
                            const dateStr = formatDate(d);
                            const lessons = byDate[dateStr] || [];
                            const isOtherMonth = d.getMonth() !== month;
                            return (
                                <td key={di} className={`print-timetable__month-cell${isOtherMonth ? " other-month" : ""}`}>
                                    <div className="print-timetable__month-day">{d.getDate()}</div>
                                    {lessons.map((e) => (
                                        <div key={e.enrollment_id} className="print-timetable__month-lesson">
                                            {formatTimeShort(e.lesson.start_time)}
                                            {e.lesson.instructor?.name ? ` ${e.lesson.instructor.name}` : ""}
                                        </div>
                                    ))}
                                </td>
                            );
                        })}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}
