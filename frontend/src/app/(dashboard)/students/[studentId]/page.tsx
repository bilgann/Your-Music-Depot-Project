"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/ui/navbar";
import DataState from "@/components/ui/data_state";
import Sections from "@/components/ui/sections";
import { useStudentDetail } from "@/features/students/hooks/use_student_detail";
import StudentInfoCard from "@/features/students/components/student_info_card";
import StudentLessonsTab from "@/features/students/components/student_lessons_tab";
import StudentInvoicesTab from "@/features/students/components/student_invoices_tab";

export default function StudentDetailPage() {
    const { studentId } = useParams() as { studentId: string };
    const { student, enrollments, invoices, loading, error } = useStudentDetail(studentId);
    const [activeSection, setActiveSection] = useState("lessons");

    return (
        <>
            <Navbar
                className="page-student-detail"
                title={student?.person?.name ?? ""}
                back={{ label: "Students", href: "/students" }}
            />
            <DataState loading={loading} error={error} empty={!student} emptyMessage="Student not found.">
                <StudentInfoCard student={student!} />

                <Sections
                    active={activeSection}
                    onChange={setActiveSection}
                    sections={[
                        { key: "lessons",  label: "Lessons",  content: <StudentLessonsTab enrollments={enrollments} /> },
                        { key: "invoices", label: "Invoices", content: <StudentInvoicesTab invoices={invoices} /> },
                    ]}
                />
            </DataState>
        </>
    );
}
