import { useEffect, useMemo, useState } from "react";
import {
    addInstructorToCourse,
    enrollStudentInCourse,
    getCourseById,
    projectCourseSchedule,
    removeInstructorFromCourse,
    unenrollStudentFromCourse,
} from "@/features/courses/api/course";
import { getInstructors } from "@/features/instructors/api/instructor";
import { getRooms } from "@/features/rooms/api/room";
import { getStudents } from "@/features/students/api/student";
import { useToast } from "@/components/ui/toast";
import type { Course, CourseOccurrence } from "@/features/courses/api/course";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { Room } from "@/features/rooms/api/room";
import type { Student } from "@/features/students/api/student";

function sortByIdOrder<T, K extends keyof T>(items: T[], ids: string[], key: K): T[] {
    return [...items].sort(
        (left, right) => ids.indexOf(String(left[key])) - ids.indexOf(String(right[key]))
    );
}

export function useCourseDetail(courseId: string) {
    const { toast } = useToast();
    const [course, setCourse] = useState<Course | null>(null);
    const [students, setStudents] = useState<Student[]>([]);
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [rooms, setRooms] = useState<Room[]>([]);
    const [occurrences, setOccurrences] = useState<CourseOccurrence[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [projecting, setProjecting] = useState(false);
    const [saving, setSaving] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [courseData, studentData, instructorData, roomData] = await Promise.all([
                getCourseById(courseId),
                getStudents(),
                getInstructors(),
                getRooms(),
            ]);
            setCourse(courseData);
            setStudents(studentData);
            setInstructors(instructorData);
            setRooms(roomData);
            setError(null);
        } catch {
            setError("Could not load course details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { void refresh(); }, [courseId]);

    const room = useMemo(
        () => rooms.find((item) => item.room_id === course?.room_id) ?? null,
        [course, rooms]
    );

    const roster = useMemo<Student[]>(() => {
        if (!course) return [];
        return sortByIdOrder(
            students.filter((student) => course.student_ids.includes(student.student_id)),
            course.student_ids,
            "student_id"
        );
    }, [course, students]);

    const assignedInstructors = useMemo<Instructor[]>(() => {
        if (!course) return [];
        return sortByIdOrder(
            instructors.filter((instructor) => course.instructor_ids.includes(instructor.instructor_id)),
            course.instructor_ids,
            "instructor_id"
        );
    }, [course, instructors]);

    const availableStudents = useMemo(() => {
        if (!course) return [];
        return students.filter((student) => !course.student_ids.includes(student.student_id));
    }, [course, students]);

    const availableInstructors = useMemo(() => {
        if (!course) return [];
        return instructors.filter((instructor) => !course.instructor_ids.includes(instructor.instructor_id));
    }, [course, instructors]);

    async function handleProjectSchedule() {
        if (!course) return;
        try {
            setProjecting(true);
            const projected = await projectCourseSchedule(course.course_id);
            setOccurrences(projected);
        } catch {
            toast("Failed to project schedule.", "error");
        } finally {
            setProjecting(false);
        }
    }

    async function handleEnrollStudent(studentId: string) {
        if (!course) return;
        try {
            setSaving(true);
            await enrollStudentInCourse(course.course_id, studentId);
            await refresh();
        } catch {
            toast("Failed to enroll student.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleUnenrollStudent(studentId: string) {
        if (!course) return;
        try {
            setSaving(true);
            await unenrollStudentFromCourse(course.course_id, studentId);
            await refresh();
        } catch {
            toast("Failed to unenroll student.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleAddInstructor(instructorId: string) {
        if (!course) return;
        try {
            setSaving(true);
            await addInstructorToCourse(course.course_id, instructorId);
            await refresh();
        } catch {
            toast("Failed to add instructor.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleRemoveInstructor(instructorId: string) {
        if (!course) return;
        try {
            setSaving(true);
            await removeInstructorFromCourse(course.course_id, instructorId);
            await refresh();
        } catch {
            toast("Failed to remove instructor.", "error");
        } finally {
            setSaving(false);
        }
    }

    return {
        course,
        room,
        roster,
        assignedInstructors,
        availableStudents,
        availableInstructors,
        occurrences,
        loading,
        error,
        projecting,
        saving,
        refresh,
        handleProjectSchedule,
        handleEnrollStudent,
        handleUnenrollStudent,
        handleAddInstructor,
        handleRemoveInstructor,
    };
}