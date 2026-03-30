"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Button from "@/components/ui/button";
import DataState from "@/components/ui/data_state";
import InfoCard from "@/components/ui/info_card";
import Navbar from "@/components/ui/navbar";
import Sections from "@/components/ui/sections";
import AttendanceModal from "@/features/scheduling/components/attendance_modal";
import LessonOccurrencesTable from "@/features/scheduling/components/lesson_occurrences_table";
import OccurrenceEnrollmentModal from "@/features/scheduling/components/occurrence_enrollment_modal";
import ScheduleLessonModal from "@/features/scheduling/components/schedule_lesson_modal";
import { useLessonDetail } from "@/features/scheduling/hooks/use_lesson_detail";

function formatTime(value: string): string {
    if (!value) return "--";
    // If it's just HH:MM or HH:MM:SS, format as a readable time
    const timeMatch = value.match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);
    if (timeMatch) {
        const h = Number(timeMatch[1]);
        const m = timeMatch[2];
        const ampm = h >= 12 ? "PM" : "AM";
        const h12 = h % 12 || 12;
        return `${h12}:${m} ${ampm}`;
    }
    // Full datetime string
    const d = new Date(value);
    if (isNaN(d.getTime())) return value;
    return d.toLocaleString([], {
        weekday: "short",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function describeCron(cron: string): string {
    const DAY_NAMES: Record<string, string> = {
        MON: "Monday", TUE: "Tuesday", WED: "Wednesday", THU: "Thursday",
        FRI: "Friday", SAT: "Saturday", SUN: "Sunday",
    };
    const parts = cron.trim().split(/\s+/);
    if (parts.length !== 5) return cron;
    const [, , dayOfMonth, , dayOfWeek] = parts;
    if (dayOfWeek !== "*") {
        const names = dayOfWeek.split(",").map((d) => DAY_NAMES[d.toUpperCase()] ?? d);
        return `Every ${names.join(", ")}`;
    }
    if (dayOfMonth !== "*") return `Monthly on the ${dayOfMonth}`;
    return cron;
}

export default function LessonDetailPage() {
    const { lessonId } = useParams() as { lessonId: string };
    const {
        lesson,
        students,
        instructors,
        rooms,
        availableStudents,
        occurrences,
        loading,
        error,
        projecting,
        saving,
        refresh,
        handleProjectSchedule,
        handleEnrollStudent,
        handleUnenrollStudent,
        handleRecordAttendance,
    } = useLessonDetail(lessonId);

    const [activeSection, setActiveSection] = useState("schedule");
    const [showEditModal, setShowEditModal] = useState(false);
    const [enrollOccurrenceId, setEnrollOccurrenceId] = useState<string | null>(null);
    const [selectedStudentId, setSelectedStudentId] = useState("");
    const [attendanceState, setAttendanceState] = useState<{
        occurrenceId: string;
        studentId: string;
        studentName: string;
        status: string;
    } | null>(null);

    const availableStudentOptions = useMemo(
        () => availableStudents.map((student) => ({ value: student.student_id, label: student.person.name })),
        [availableStudents]
    );

    const instructorName = useMemo(
        () => instructors.find((i) => i.instructor_id === lesson?.instructor_id)?.name ?? lesson?.instructor_id ?? "--",
        [instructors, lesson]
    );

    const roomName = useMemo(
        () => rooms.find((r) => r.room_id === lesson?.room_id)?.name ?? lesson?.room_id ?? "--",
        [rooms, lesson]
    );

    const enrolledStudents = useMemo(() => {
        if (!lesson?.student_ids?.length) return [];
        const studentById = Object.fromEntries(students.map((s) => [s.student_id, s]));
        return lesson.student_ids.map((id) => studentById[id]).filter(Boolean);
    }, [lesson, students]);

    async function handleEnrollSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!enrollOccurrenceId || !selectedStudentId) return;
        await handleEnrollStudent(enrollOccurrenceId, selectedStudentId);
        setSelectedStudentId("");
        setEnrollOccurrenceId(null);
    }

    async function handleAttendanceSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!attendanceState) return;
        await handleRecordAttendance(attendanceState.occurrenceId, attendanceState.studentId, attendanceState.status);
        setAttendanceState(null);
    }

    const recurrenceDisplay = lesson?.recurrence
        ? describeCron(lesson.recurrence)
        : "One-time lesson";

    return (
        <>
            <Navbar
                className="page-lesson-detail"
                title={lesson ? `${instructorName} — ${roomName}` : ""}
                back={{ label: "Dashboard", href: "/home" }}
                actions={lesson ? <Button variant="primary" onClick={() => setShowEditModal(true)}>Edit Lesson</Button> : undefined}
            />
            <DataState loading={loading} error={error} empty={!lesson} emptyMessage="Lesson not found.">
                {lesson && (
                    <>
                        <InfoCard
                            rows={[
                                { label: "Instructor", value: instructorName },
                                { label: "Room", value: roomName },
                                { label: "Start", value: formatTime(lesson.start_time) },
                                { label: "End", value: formatTime(lesson.end_time) },
                                {
                                    label: "Status",
                                    value: (
                                        <span className={`status-badge status-${(lesson.status ?? "scheduled").toLowerCase()}`}>
                                            {lesson.status || "Scheduled"}
                                        </span>
                                    ),
                                },
                                { label: "Recurrence", value: recurrenceDisplay },
                                ...(lesson.rate ? [{ label: "Rate", value: `$${Number(lesson.rate).toFixed(2)}` }] : []),
                            ]}
                        />

                        <Sections
                            active={activeSection}
                            onChange={setActiveSection}
                            sections={[
                                {
                                    key: "students",
                                    label: `Students (${enrolledStudents.length})`,
                                    content: enrolledStudents.length === 0 ? (
                                        <p className="table-empty">No students enrolled in this lesson.</p>
                                    ) : (
                                        <div className="data-table-wrapper">
                                            <table className="data-table">
                                                <thead>
                                                    <tr>
                                                        <th>Name</th>
                                                        <th>Email</th>
                                                        <th>Phone</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {enrolledStudents.map((student) => (
                                                        <tr key={student.student_id}>
                                                            <td>{student.person.name}</td>
                                                            <td>{student.person.email || "--"}</td>
                                                            <td>{student.person.phone || "--"}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    ),
                                },
                                {
                                    key: "schedule",
                                    label: "Projected Schedule",
                                    content: (
                                        <LessonOccurrencesTable
                                            occurrences={occurrences}
                                            projecting={projecting}
                                            saving={saving}
                                            onProject={handleProjectSchedule}
                                            onOpenEnroll={(occurrenceId) => setEnrollOccurrenceId(occurrenceId)}
                                            onOpenAttendance={(occurrenceId, studentId, studentName, currentStatus) => setAttendanceState({
                                                occurrenceId,
                                                studentId,
                                                studentName,
                                                status: currentStatus || "Present",
                                            })}
                                            onUnenroll={(occurrenceId, studentId) => void handleUnenrollStudent(occurrenceId, studentId)}
                                        />
                                    ),
                                },
                            ]}
                        />
                    </>
                )}
            </DataState>

            {showEditModal && lesson && (
                <ScheduleLessonModal
                    existingLesson={lesson}
                    onSaved={() => { setShowEditModal(false); void refresh(); }}
                    onClose={() => setShowEditModal(false)}
                />
            )}

            {enrollOccurrenceId && (
                <OccurrenceEnrollmentModal
                    selectedStudentId={selectedStudentId}
                    studentOptions={availableStudentOptions}
                    saving={saving}
                    onChange={setSelectedStudentId}
                    onClose={() => {
                        setSelectedStudentId("");
                        setEnrollOccurrenceId(null);
                    }}
                    onSubmit={handleEnrollSubmit}
                />
            )}

            {attendanceState && (
                <AttendanceModal
                    studentName={attendanceState.studentName}
                    value={attendanceState.status}
                    saving={saving}
                    onChange={(status) => setAttendanceState({ ...attendanceState, status })}
                    onClose={() => setAttendanceState(null)}
                    onSubmit={handleAttendanceSubmit}
                />
            )}
        </>
    );
}
