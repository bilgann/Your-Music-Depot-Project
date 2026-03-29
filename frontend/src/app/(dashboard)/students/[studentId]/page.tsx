"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import DataState from "@/components/ui/data_state";
import Sections from "@/components/ui/sections";
import { useStudentDetail } from "@/features/students/hooks/use_student_detail";
import StudentInfoCard from "@/features/students/components/student_info_card";
import StudentLessonsTab from "@/features/students/components/student_lessons_tab";
import StudentInvoicesTab from "@/features/students/components/student_invoices_tab";

export default function StudentDetailPage() {
    const { studentId } = useParams() as { studentId: string };
    const router = useRouter();
    const { student, enrollments, invoices, loading, error } = useStudentDetail(studentId);
    const [activeSection, setActiveSection] = useState("lessons");

    return (
        <main className="page-student-detail">
            <DataState loading={loading} error={error} empty={!student} emptyMessage="Student not found.">
                <div className="page-header">
                    <div className="client-detail-back">
                        <button className="btn-back" onClick={() => router.push("/students")}>&#8592; Students</button>
                        <h1>{student?.person.name}</h1>
                    </div>
                </div>

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
        </main>
    );
}
