"use client";

import { useRouter } from "next/navigation";
import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import Navbar from "@/components/ui/navbar";
import CourseModal from "@/features/courses/components/course_modal";
import { useCourseCrud } from "@/features/courses/hooks/use_course_crud";
import { useCourses } from "@/features/courses/hooks/use_courses";
import type { Course } from "@/features/courses/api/course";

function formatPeriod(course: Course) {
    return `${course.period_start} to ${course.period_end}`;
}

export default function CoursesPage() {
    const router = useRouter();
    const { courses, instructors, loading, error, refresh, page, setPage, search, setSearch, pageCount } = useCourses();
    const { showModal, setShowModal, editing, form, setForm, saving, rooms, openAdd, openEdit, handleSubmit, handleDelete, instructors: instructorOptions } = useCourseCrud(refresh);

    function getLeadInstructorName(course: Course) {
        return instructors.find((instructor) => instructor.instructor_id === course.instructor_ids[0])?.name ?? "--";
    }

    return (
        <>
            <Navbar
                title="Courses"
                className="page-courses"
                search={search}
                onSearchChange={setSearch}
                actions={<Button variant="primary" onClick={openAdd}>+ Add Course</Button>}
            />
            <DataTable
                loading={loading}
                error={error}
                data={courses}
                emptyMessage="No courses found. Create one to get started."
                getKey={(course) => course.course_id}
                columns={[
                    { header: "Name", render: (course) => course.name },
                    { header: "Instructor", render: (course) => getLeadInstructorName(course) },
                    { header: "Period", render: (course) => formatPeriod(course) },
                    { header: "Status", render: (course) => course.status },
                    { header: "Enrolled / Capacity", render: (course) => `${course.student_ids.length} / ${course.capacity ?? "--"}` },
                ]}
                onEdit={openEdit}
                onDelete={handleDelete}
                onRowClick={(course) => router.push(`/courses/${course.course_id}`)}
                page={page}
                pageCount={pageCount}
                onPageChange={setPage}
            />
            {showModal && (
                <CourseModal
                    title={editing ? "Update Course" : "Create Course"}
                    form={form}
                    roomOptions={rooms}
                    instructorOptions={instructorOptions}
                    saving={saving}
                    onClose={() => setShowModal(false)}
                    onSubmit={handleSubmit}
                    onChange={setForm}
                />
            )}
        </>
    );
}