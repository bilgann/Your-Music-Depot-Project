import { useEffect, useMemo, useState } from "react";
import { getStudents } from "@/features/students/api/student";
import {
    addCredential,
    buildInstructorStudents,
    getCoursesByInstructor,
    getInstructorById,
    getInstructorCompatibility,
    getInstructorCredentials,
    getInstructorLessons,
    removeCredential,
    updateInstructorBlockedTimes,
} from "@/features/instructors/api/instructor_detail";
import { useToast } from "@/components/ui/toast";
import type { Student } from "@/features/students/api/student";
import type {
    Credential,
    InstructorCompatibility,
    InstructorDetail,
    InstrumentProficiency,
} from "@/features/instructors/api/instructor_detail";
import type { BlockedTime, Lesson } from "@/types/index";

export type BlockedTimeFormState = {
    label: string;
    block_type: string;
    start_date: string;
    end_date: string;
    recurrence_mode: "none" | "recurring";
    recurrence: string;
};

const emptyBlockedTimeForm: BlockedTimeFormState = {
    label: "",
    block_type: "other",
    start_date: "",
    end_date: "",
    recurrence_mode: "none",
    recurrence: "",
};

function toBlockedTimePayload(form: BlockedTimeFormState): BlockedTime {
    if (form.recurrence_mode === "recurring" && form.recurrence) {
        return {
            label: form.label,
            block_type: form.block_type,
            recurrence: { rule_type: "cron", value: form.recurrence },
        };
    }
    if (form.start_date && form.end_date && form.start_date !== form.end_date) {
        return {
            label: form.label,
            block_type: form.block_type,
            date_range: { period_start: form.start_date, period_end: form.end_date },
        };
    }
    return {
        label: form.label,
        block_type: form.block_type,
        date: form.start_date || form.end_date,
    };
}

export type CredentialFormState = {
    credential_type: string;
    issued_by: string;
    issued_date: string;
    valid_from: string;
    valid_until: string;
    proficiencies: InstrumentProficiency[];
};

const emptyCredentialForm: CredentialFormState = {
    credential_type: "musical",
    issued_by: "",
    issued_date: "",
    valid_from: "",
    valid_until: "",
    proficiencies: [{ name: "", family: "other", min_level: "beginner", max_level: "professional" }],
};

function sortLessons(lessons: Lesson[]) {
    return [...lessons].sort((left, right) => left.start_time.localeCompare(right.start_time));
}

function dedupeStudents(students: Student[]) {
    const seen = new Set<string>();
    return students.filter((student) => {
        if (seen.has(student.student_id)) return false;
        seen.add(student.student_id);
        return true;
    });
}

export function useInstructorDetail(instructorId: string) {
    const { toast } = useToast();
    const [instructor, setInstructor] = useState<InstructorDetail | null>(null);
    const [credentials, setCredentials] = useState<Credential[]>([]);
    const [lessons, setLessons] = useState<Lesson[]>([]);
    const [students, setStudents] = useState<Student[]>([]);
    const [compatibility, setCompatibility] = useState<InstructorCompatibility[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCredentialModal, setShowCredentialModal] = useState(false);
    const [credentialForm, setCredentialForm] = useState<CredentialFormState>(emptyCredentialForm);
    const [savingCredential, setSavingCredential] = useState(false);
    const [showBlockedTimeModal, setShowBlockedTimeModal] = useState(false);
    const [blockedTimeForm, setBlockedTimeForm] = useState<BlockedTimeFormState>(emptyBlockedTimeForm);
    const [savingBlockedTime, setSavingBlockedTime] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [instructorData, credentialData, lessonData, studentData, courseData] = await Promise.all([
                getInstructorById(instructorId),
                getInstructorCredentials(instructorId),
                getInstructorLessons(),
                getStudents(),
                getCoursesByInstructor(instructorId),
            ]);

            const instructorStudents = dedupeStudents(buildInstructorStudents(courseData, studentData));
            const compatibilityResults = await Promise.all(
                instructorStudents.map(async (student) => {
                    try {
                        const result = await getInstructorCompatibility(student.student_id, instructorId);
                        return {
                            student_id: student.student_id,
                            student_name: student.person.name,
                            ...result,
                        };
                    } catch {
                        return {
                            student_id: student.student_id,
                            student_name: student.person.name,
                            can_assign: false,
                            hard_verdict: null,
                            soft_verdict: null,
                            reasons: ["Compatibility check unavailable."],
                        };
                    }
                })
            );

            setInstructor(instructorData);
            setCredentials(credentialData);
            setLessons(sortLessons(lessonData.filter((lesson) => lesson.instructor_id === instructorId)));
            setStudents(instructorStudents);
            setCompatibility(compatibilityResults);
            setError(null);
        } catch {
            setError("Could not load instructor details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { void refresh(); }, [instructorId]);

    const upcomingLessons = useMemo(
        () => lessons.filter((lesson) => new Date(lesson.start_time).getTime() >= Date.now()),
        [lessons]
    );

    function openCredentialModal() {
        setCredentialForm(emptyCredentialForm);
        setShowCredentialModal(true);
    }

    async function handleCredentialSubmit(e: React.FormEvent) {
        e.preventDefault();
        setSavingCredential(true);
        try {
            await addCredential({
                instructor_id: instructorId,
                credential_type: credentialForm.credential_type,
                ...(credentialForm.issued_by && { issued_by: credentialForm.issued_by }),
                ...(credentialForm.issued_date && { issued_date: credentialForm.issued_date }),
                ...(credentialForm.valid_from && { valid_from: credentialForm.valid_from }),
                ...(credentialForm.valid_until && { valid_until: credentialForm.valid_until }),
                ...(credentialForm.proficiencies.filter((item) => item.name).length > 0 && {
                    proficiencies: credentialForm.proficiencies.filter((item) => item.name),
                }),
            });
            setShowCredentialModal(false);
            await refresh();
        } catch {
            toast("Failed to save credential.", "error");
        } finally {
            setSavingCredential(false);
        }
    }

    async function handleCredentialDelete(credentialId: string) {
        if (!confirm("Delete this credential?")) return;
        try {
            await removeCredential(credentialId);
            await refresh();
        } catch {
            toast("Failed to delete credential.", "error");
        }
    }

    const blockedTimes = instructor?.blocked_times ?? [];

    function openBlockedTimeModal() {
        setBlockedTimeForm(emptyBlockedTimeForm);
        setShowBlockedTimeModal(true);
    }

    async function handleBlockedTimeSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!instructor) return;
        setSavingBlockedTime(true);
        try {
            const next = [...blockedTimes, toBlockedTimePayload(blockedTimeForm)];
            const updated = await updateInstructorBlockedTimes(instructorId, next);
            setInstructor(updated);
            setShowBlockedTimeModal(false);
        } catch {
            toast("Failed to save blocked time.", "error");
        } finally {
            setSavingBlockedTime(false);
        }
    }

    async function handleBlockedTimeDelete(index: number) {
        if (!instructor) return;
        if (!confirm("Delete this blocked time?")) return;
        try {
            const next = blockedTimes.filter((_, i) => i !== index);
            const updated = await updateInstructorBlockedTimes(instructorId, next);
            setInstructor(updated);
        } catch {
            toast("Failed to delete blocked time.", "error");
        }
    }

    return {
        instructor,
        credentials,
        schedule: upcomingLessons,
        students,
        compatibility,
        loading,
        error,
        refresh,
        showCredentialModal,
        setShowCredentialModal,
        credentialForm,
        setCredentialForm,
        savingCredential,
        openCredentialModal,
        handleCredentialSubmit,
        handleCredentialDelete,
        blockedTimes,
        showBlockedTimeModal,
        setShowBlockedTimeModal,
        blockedTimeForm,
        setBlockedTimeForm,
        savingBlockedTime,
        openBlockedTimeModal,
        handleBlockedTimeSubmit,
        handleBlockedTimeDelete,
    };
}