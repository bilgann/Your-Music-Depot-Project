"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import DataState from "@/components/ui/data_state";
import Navbar from "@/components/ui/navbar";
import CourseDetailTabs from "@/features/courses/components/course_detail_tabs";
import CourseInfoCard from "@/features/courses/components/course_info_card";
import EnrollStudentModal from "@/features/courses/components/enroll_student_modal";
import { useCourseDetail } from "@/features/courses/hooks/use_course_detail";

export default function CourseDetailPage() {
    const { courseId } = useParams() as { courseId: string };
    const {
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
        handleProjectSchedule,
        handleEnrollStudent,
        handleUnenrollStudent,
        handleAddInstructor,
        handleRemoveInstructor,
    } = useCourseDetail(courseId);
    const [activeSection, setActiveSection] = useState("roster");
    const [showEnrollModal, setShowEnrollModal] = useState(false);
    const [selectedStudentId, setSelectedStudentId] = useState("");

    const availableStudentOptions = useMemo(
        () => availableStudents.map((student) => ({ value: student.student_id, label: student.person.name })),
        [availableStudents]
    );

    const availableInstructorOptions = useMemo(
        () => availableInstructors.map((instructor) => ({ value: instructor.instructor_id, label: instructor.name })),
        [availableInstructors]
    );

    async function handleSubmitEnroll(e: React.FormEvent) {
        e.preventDefault();
        if (!selectedStudentId) return;
        await handleEnrollStudent(selectedStudentId);
        setSelectedStudentId("");
        setShowEnrollModal(false);
    }

    return (
        <>
            <Navbar
                className="page-course-detail"
                title={course?.name ?? ""}
                back={{ label: "Courses", href: "/courses" }}
            />
            <DataState loading={loading} error={error} empty={!course} emptyMessage="Course not found.">
                {course && (
                    <>
                        <CourseInfoCard
                            course={course}
                            roomName={room?.name ?? "--"}
                            leadInstructorName={assignedInstructors[0]?.name ?? "--"}
                        />
                        <CourseDetailTabs
                            active={activeSection}
                            onChange={setActiveSection}
                            course={course}
                            roster={roster}
                            assignedInstructors={assignedInstructors}
                            availableInstructorOptions={availableInstructorOptions}
                            occurrences={occurrences}
                            saving={saving}
                            projecting={projecting}
                            onOpenEnrollModal={() => setShowEnrollModal(true)}
                            onUnenrollStudent={handleUnenrollStudent}
                            onProjectSchedule={handleProjectSchedule}
                            onAddInstructor={handleAddInstructor}
                            onRemoveInstructor={handleRemoveInstructor}
                        />
                    </>
                )}
            </DataState>
            {showEnrollModal && (
                <EnrollStudentModal
                    selectedStudentId={selectedStudentId}
                    studentOptions={availableStudentOptions}
                    saving={saving}
                    onChange={setSelectedStudentId}
                    onClose={() => {
                        setSelectedStudentId("");
                        setShowEnrollModal(false);
                    }}
                    onSubmit={handleSubmitEnroll}
                />
            )}
        </>
    );
}