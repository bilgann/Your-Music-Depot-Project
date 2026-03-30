import { useEffect, useMemo, useState } from "react";
import { getInstructors } from "@/features/instructors/api/instructor";
import { getRooms } from "@/features/rooms/api/room";
import { getStudents } from "@/features/students/api/student";
import {
    enrollInOccurrence,
    getLessonById,
    getLessonOccurrences,
    getOccurrenceStudents,
    projectLessonSchedule,
    recordAttendance,
    unenrollFromOccurrence,
} from "@/features/scheduling/api/lesson";
import { useToast } from "@/components/ui/toast";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { Room } from "@/features/rooms/api/room";
import type { Student } from "@/features/students/api/student";
import type { Lesson } from "@/types/index";
import type { LessonOccurrence, OccurrenceEnrollment } from "@/features/scheduling/api/lesson";

function attachStudentNames(occurrences: LessonOccurrence[], students: Student[]): LessonOccurrence[] {
    const nameById = Object.fromEntries(students.map((student) => [student.student_id, student.person.name]));
    return occurrences.map((occurrence) => ({
        ...occurrence,
        enrollments: (occurrence.enrollments ?? []).map((enrollment) => ({
            ...enrollment,
            student_name: nameById[enrollment.student_id] ?? enrollment.student_id,
        })),
    }));
}

export function useLessonDetail(lessonId: string) {
    const { toast } = useToast();
    const [lesson, setLesson] = useState<Lesson | null>(null);
    const [students, setStudents] = useState<Student[]>([]);
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [rooms, setRooms] = useState<Room[]>([]);
    const [occurrences, setOccurrences] = useState<LessonOccurrence[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [projecting, setProjecting] = useState(false);
    const [saving, setSaving] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [lessonData, studentData, instructorData, roomData, occurrenceData] = await Promise.all([
                getLessonById(lessonId),
                getStudents(),
                getInstructors(),
                getRooms(),
                getLessonOccurrences(lessonId),
            ]);
            setLesson(lessonData);
            setStudents(studentData);
            setInstructors(instructorData);
            setRooms(roomData);
            setOccurrences(attachStudentNames(occurrenceData, studentData));
            setError(null);
        } catch {
            setError("Could not load lesson details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { void refresh(); }, [lessonId]);

    const availableStudents = useMemo(() => {
        const enrolledIds = new Set(occurrences.flatMap((occurrence) => occurrence.enrollments?.map((item) => item.student_id) ?? []));
        return students.filter((student) => !enrolledIds.has(student.student_id));
    }, [occurrences, students]);

    async function handleProjectSchedule() {
        if (!lesson?.recurrence) {
            toast("Cannot project: lesson has no recurrence rule. Edit the lesson to add one.", "error");
            return;
        }
        try {
            setProjecting(true);
            const projected = await projectLessonSchedule(lessonId);
            setOccurrences(attachStudentNames(projected, students));
        } catch (err) {
            const msg = err instanceof Error ? err.message : "Failed to project lesson schedule.";
            toast(msg, "error");
        } finally {
            setProjecting(false);
        }
    }

    async function refreshOccurrenceEnrollments(occurrenceId: string) {
        const nameById = Object.fromEntries(students.map((student) => [student.student_id, student.person.name]));
        const enrollments = await getOccurrenceStudents(occurrenceId);
        setOccurrences((current) => current.map((occurrence) => {
            if (occurrence.occurrence_id !== occurrenceId) return occurrence;
            const nextEnrollments: OccurrenceEnrollment[] = enrollments.map((enrollment) => ({
                ...enrollment,
                student_name: nameById[enrollment.student_id] ?? enrollment.student_id,
            }));
            return { ...occurrence, enrollments: nextEnrollments };
        }));
    }

    async function handleEnrollStudent(occurrenceId: string, studentId: string) {
        try {
            setSaving(true);
            await enrollInOccurrence(occurrenceId, studentId);
            await refreshOccurrenceEnrollments(occurrenceId);
        } catch {
            toast("Failed to enroll student.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleUnenrollStudent(occurrenceId: string, studentId: string) {
        try {
            setSaving(true);
            await unenrollFromOccurrence(occurrenceId, studentId);
            await refreshOccurrenceEnrollments(occurrenceId);
        } catch {
            toast("Failed to unenroll student.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleRecordAttendance(occurrenceId: string, studentId: string, attendanceStatus: string) {
        try {
            setSaving(true);
            await recordAttendance(occurrenceId, studentId, attendanceStatus);
            await refreshOccurrenceEnrollments(occurrenceId);
        } catch {
            toast("Failed to record attendance.", "error");
        } finally {
            setSaving(false);
        }
    }

    return {
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
    };
}