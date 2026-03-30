"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import DataState from "@/components/ui/data_state";
import InfoCard from "@/components/ui/info_card";
import Navbar from "@/components/ui/navbar";
import AttendanceModal from "@/features/scheduling/components/attendance_modal";
import LessonOccurrencesTable from "@/features/scheduling/components/lesson_occurrences_table";
import OccurrenceEnrollmentModal from "@/features/scheduling/components/occurrence_enrollment_modal";
import { useLessonDetail } from "@/features/scheduling/hooks/use_lesson_detail";

export default function LessonDetailPage() {
    const { lessonId } = useParams() as { lessonId: string };
    const {
        lesson,
        availableStudents,
        occurrences,
        loading,
        error,
        projecting,
        saving,
        handleProjectSchedule,
        handleEnrollStudent,
        handleUnenrollStudent,
        handleRecordAttendance,
    } = useLessonDetail(lessonId);
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

    return (
        <>
            <Navbar
                className="page-lesson-detail"
                title={lesson ? `Lesson ${lesson.lesson_id}` : ""}
                back={{ label: "Dashboard", href: "/home" }}
            />
            <DataState loading={loading} error={error} empty={!lesson} emptyMessage="Lesson not found.">
                {lesson && (
                    <>
                        <InfoCard
                            rows={[
                                { label: "Instructor", value: lesson.instructor_id },
                                { label: "Room", value: lesson.room_id },
                                { label: "Start", value: lesson.start_time },
                                { label: "End", value: lesson.end_time },
                                { label: "Status", value: lesson.status || "--" },
                                { label: "Recurrence", value: lesson.recurrence || "--" },
                            ]}
                        />
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
                    </>
                )}
            </DataState>

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