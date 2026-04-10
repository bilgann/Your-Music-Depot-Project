"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { faPrint } from "@fortawesome/free-solid-svg-icons";
import Navbar from "@/components/ui/navbar";
import Button from "@/components/ui/button";
import DataState from "@/components/ui/data_state";
import Sections from "@/components/ui/sections";
import BlockedTimeModal from "@/features/rooms/components/blocked_time_modal";
import CompatibilityOverrideModal from "@/features/students/components/compatibility_override_modal";
import StudentBlockedTimesTab from "@/features/students/components/student_blocked_times_tab";
import StudentCompatibilityTab from "@/features/students/components/student_compatibility_tab";
import { useStudentDetail } from "@/features/students/hooks/use_student_detail";
import StudentInfoCard from "@/features/students/components/student_info_card";
import StudentLessonsTab from "@/features/students/components/student_lessons_tab";
import StudentInvoicesTab from "@/features/students/components/student_invoices_tab";
import StudentRequirementsTab from "@/features/students/components/student_requirements_tab";
import StudentInstrumentsTab from "@/features/students/components/student_instruments_tab";
import PrintTimetableModal from "@/features/students/components/print_timetable_modal";

export default function StudentDetailPage() {
    const { studentId } = useParams() as { studentId: string };
    const {
        student,
        enrollments,
        invoices,
        compatibility,
        loading,
        error,
        savingRequirements,
        handleUpdateRequirements,
        savingSkillLevels,
        handleUpdateInstrumentSkillLevels,
        showCompatibilityModal,
        setShowCompatibilityModal,
        compatibilityForm,
        setCompatibilityForm,
        savingCompatibility,
        instructorOptions,
        openCompatibilityModal,
        handleCompatibilitySubmit,
        blockedTimes,
        showBlockedTimeModal,
        setShowBlockedTimeModal,
        blockedTimeForm,
        setBlockedTimeForm,
        savingBlockedTime,
        openBlockedTimeModal,
        handleBlockedTimeSubmit,
        handleBlockedTimeDelete,
    } = useStudentDetail(studentId);
    const [activeSection, setActiveSection] = useState("lessons");
    const [showTimetable, setShowTimetable] = useState(false);

    return (
        <>
            <Navbar
                className="page-student-detail"
                title={student?.person?.name ?? ""}
                back={{ label: "Students", href: "/students" }}
                actions={student && (
                    <Button variant="secondary" icon={faPrint} onClick={() => setShowTimetable(true)}>Print Timetable</Button>
                )}
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
                            key: "instruments",
                            label: "Instruments",
                            content: (
                                <StudentInstrumentsTab
                                    instrumentSkillLevels={student?.instrument_skill_levels ?? []}
                                    saving={savingSkillLevels}
                                    onSave={handleUpdateInstrumentSkillLevels}
                                />
                            ),
                        },
                        {
                            key: "requirements",
                            label: "Requirements",
                            content: (
                                <StudentRequirementsTab
                                    requirements={student?.requirements ?? []}
                                    saving={savingRequirements}
                                    onSave={handleUpdateRequirements}
                                />
                            ),
                        },
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
                        {
                            key: "blocked-times",
                            label: "Blocked Times",
                            content: (
                                <StudentBlockedTimesTab
                                    blockedTimes={blockedTimes}
                                    onAdd={openBlockedTimeModal}
                                    onDelete={handleBlockedTimeDelete}
                                />
                            ),
                        },
                    ]}
                />
            </DataState>
            {showTimetable && student && (
                <PrintTimetableModal
                    studentName={student.person.name}
                    enrollments={enrollments}
                    onClose={() => setShowTimetable(false)}
                />
            )}
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
            {showBlockedTimeModal && (
                <BlockedTimeModal
                    form={blockedTimeForm}
                    saving={savingBlockedTime}
                    onChange={(form) => setBlockedTimeForm(form)}
                    onClose={() => setShowBlockedTimeModal(false)}
                    onSubmit={handleBlockedTimeSubmit}
                />
            )}
        </>
    );
}
