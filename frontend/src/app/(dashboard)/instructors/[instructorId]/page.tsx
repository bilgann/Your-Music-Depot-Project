"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import DataState from "@/components/ui/data_state";
import Navbar from "@/components/ui/navbar";
import CredentialModal from "@/features/instructors/components/credential_modal";
import InstructorDetailTabs from "@/features/instructors/components/instructor_detail_tabs";
import InstructorInfoCard from "@/features/instructors/components/instructor_info_card";
import { useInstructorDetail } from "@/features/instructors/hooks/use_instructor_detail";

export default function InstructorDetailPage() {
    const { instructorId } = useParams() as { instructorId: string };
    const {
        instructor,
        credentials,
        schedule,
        students,
        compatibility,
        loading,
        error,
        showCredentialModal,
        setShowCredentialModal,
        credentialForm,
        setCredentialForm,
        savingCredential,
        openCredentialModal,
        handleCredentialSubmit,
        handleCredentialDelete,
    } = useInstructorDetail(instructorId);
    const [activeSection, setActiveSection] = useState("credentials");

    return (
        <>
            <Navbar
                className="page-instructor-detail"
                title={instructor?.name ?? ""}
                back={{ label: "Instructors", href: "/instructors" }}
            />
            <DataState loading={loading} error={error} empty={!instructor} emptyMessage="Instructor not found.">
                {instructor && (
                    <>
                        <InstructorInfoCard instructor={instructor} />
                        <InstructorDetailTabs
                            active={activeSection}
                            onChange={setActiveSection}
                            credentials={credentials}
                            schedule={schedule}
                            students={students}
                            compatibility={compatibility}
                            onAddCredential={openCredentialModal}
                            onDeleteCredential={handleCredentialDelete}
                        />
                    </>
                )}
            </DataState>
            {showCredentialModal && (
                <CredentialModal
                    form={credentialForm}
                    saving={savingCredential}
                    onChange={setCredentialForm}
                    onClose={() => setShowCredentialModal(false)}
                    onSubmit={handleCredentialSubmit}
                />
            )}
        </>
    );
}