import { useEffect, useMemo, useState } from "react";
import { getStudents } from "@/features/students/api/student";
import {
    enrollInOccurrence,
    getLessonById,
    getOccurrenceStudents,
    projectLessonSchedule,
    recordAttendance,
    unenrollFromOccurrence,
} from "@/features/scheduling/api/lesson";
import { useToast } from "@/components/ui/toast";
import type { Student } from "@/features/students/api/student";
import type { Lesson } from "@/types/index";
import type { LessonOccurrence, OccurrenceEnrollment } from "@/features/scheduling/api/lesson";

async function attachOccurrenceEnrollments(occurrences: LessonOccurrence[], students: Student[]): Promise<LessonOccurrence[]> {
    const nameById = Object.fromEntries(students.map((student) => [student.student_id, student.person.name]));

    const withEnrollments = await Promise.all(
        occurrences.map(async (occurrence) => {
            try {
                const enrollments = await getOccurrenceStudents(occurrence.occurrence_id);
                return {
                    ...occurrence,
                    enrollments: enrollments.map((enrollment) => ({
                        ...enrollment,
                        student_name: nameById[enrollment.student_id] ?? enrollment.student_id,
                    })),
                };
            } catch {
                return { ...occurrence, enrollments: [] };
            }
        })
    );

    return withEnrollments;
}

export function useLessonDetail(lessonId: string) {
    const { toast } = useToast();
    const [lesson, setLesson] = useState<Lesson | null>(null);
    const [students, setStudents] = useState<Student[]>([]);
    const [occurrences, setOccurrences] = useState<LessonOccurrence[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [projecting, setProjecting] = useState(false);
    const [saving, setSaving] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [lessonData, studentData] = await Promise.all([
                getLessonById(lessonId),
                getStudents(),
            ]);
            setLesson(lessonData);
            setStudents(studentData);
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
        try {
            setProjecting(true);
            const projected = await projectLessonSchedule(lessonId);
            const withEnrollments = await attachOccurrenceEnrollments(projected, students);
            setOccurrences(withEnrollments);
        } catch {
            toast("Failed to project lesson schedule.", "error");
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