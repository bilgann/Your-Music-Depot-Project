"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/ui/navbar";
import DataState from "@/components/ui/data_state";
import Sections from "@/components/ui/sections";
import CompatibilityOverrideModal from "@/features/students/components/compatibility_override_modal";
import StudentCompatibilityTab from "@/features/students/components/student_compatibility_tab";
import { useStudentDetail } from "@/features/students/hooks/use_student_detail";
import StudentInfoCard from "@/features/students/components/student_info_card";
import StudentLessonsTab from "@/features/students/components/student_lessons_tab";
import StudentInvoicesTab from "@/features/students/components/student_invoices_tab";

export default function StudentDetailPage() {
    const { studentId } = useParams() as { studentId: string };
    const {
        student,
        enrollments,
        invoices,
        compatibility,
        loading,
        error,
        showCompatibilityModal,
        setShowCompatibilityModal,
        compatibilityForm,
        setCompatibilityForm,
        savingCompatibility,
        instructorOptions,
        openCompatibilityModal,
        handleCompatibilitySubmit,
    } = useStudentDetail(studentId);
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
                        {
                            key: "compatibility",
                            label: "Compatibility",
                            content: (
                                <StudentCompatibilityTab
                                    items={compatibility}
                                    onAddOverride={() => openCompatibilityModal()}
                                    onEditOverride={(instructorId) => openCompatibilityModal(instructorId)}
                                />
                            ),
                        },
                    ]}
                />
            </DataState>
            {showCompatibilityModal && student ? (
                <CompatibilityOverrideModal
                    form={compatibilityForm}
                    saving={savingCompatibility}
                    instructorOptions={instructorOptions}
                    onChange={setCompatibilityForm}
                    onClose={() => setShowCompatibilityModal(false)}
                    onSubmit={handleCompatibilitySubmit}
                />
            ) : null}
        </>
    );
}
