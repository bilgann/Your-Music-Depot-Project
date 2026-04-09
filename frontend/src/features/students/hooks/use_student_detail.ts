import { useEffect, useMemo, useState } from "react";
import { getInstructors } from "@/features/instructors/api/instructor";
import { addCompatibilityOverride, checkCompatibility } from "@/features/students/api/compatibility";
import { getStudentById, getStudentLessons, getStudentInvoices, updateStudent, updateStudentBlockedTimes } from "@/features/students/api/student";
import { useToast } from "@/components/ui/toast";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { StudentCompatibilityItem } from "@/features/students/api/compatibility";
import type { Student, StudentEnrollment, StudentInvoice, TeachingRequirement, InstrumentSkillLevel } from "@/features/students/api/student";
import type { BlockedTime } from "@/types/index";

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

export type CompatibilityOverrideFormState = {
    instructor_id: string;
    verdict: string;
    reason: string;
};

const emptyCompatibilityForm: CompatibilityOverrideFormState = {
    instructor_id: "",
    verdict: "preferred",
    reason: "",
};

function sortCompatibility(items: StudentCompatibilityItem[]) {
    const priority: Record<string, number> = {
        required: 0,
        preferred: 1,
        ok: 2,
        disliked: 3,
        blocked: 4,
    };

    function getVerdict(item: StudentCompatibilityItem) {
        if (!item.can_assign) return "blocked";
        return item.hard_verdict ?? item.soft_verdict ?? "ok";
    }

    return [...items].sort((left, right) => {
        const priorityDelta = priority[getVerdict(left)] - priority[getVerdict(right)];
        if (priorityDelta !== 0) return priorityDelta;
        return left.instructor_name.localeCompare(right.instructor_name);
    });
}

export function useStudentDetail(studentId: string) {
    const { toast } = useToast();
    const [student, setStudent] = useState<Student | null>(null);
    const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
    const [invoices, setInvoices] = useState<StudentInvoice[]>([]);
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [compatibility, setCompatibility] = useState<StudentCompatibilityItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCompatibilityModal, setShowCompatibilityModal] = useState(false);
    const [compatibilityForm, setCompatibilityForm] = useState<CompatibilityOverrideFormState>(emptyCompatibilityForm);
    const [savingCompatibility, setSavingCompatibility] = useState(false);
    const [savingRequirements, setSavingRequirements] = useState(false);
    const [savingSkillLevels, setSavingSkillLevels] = useState(false);
    const [showBlockedTimeModal, setShowBlockedTimeModal] = useState(false);
    const [blockedTimeForm, setBlockedTimeForm] = useState<BlockedTimeFormState>(emptyBlockedTimeForm);
    const [savingBlockedTime, setSavingBlockedTime] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [studentData, lessonsData, invoicesData, instructorData] = await Promise.all([
                getStudentById(studentId),
                getStudentLessons(studentId),
                getStudentInvoices(studentId),
                getInstructors(),
            ]);
            const compatibilityData = await Promise.all(
                instructorData.map(async (instructor) => {
                    try {
                        const result = await checkCompatibility(studentId, instructor.instructor_id);
                        return {
                            instructor_id: instructor.instructor_id,
                            instructor_name: instructor.name,
                            ...result,
                        };
                    } catch {
                        return {
                            instructor_id: instructor.instructor_id,
                            instructor_name: instructor.name,
                            can_assign: false,
                            hard_verdict: null,
                            soft_verdict: null,
                            reasons: ["Compatibility check unavailable."],
                        };
                    }
                })
            );
            setStudent(studentData);
            setEnrollments(lessonsData);
            setInvoices(invoicesData);
            setInstructors(instructorData);
            setCompatibility(sortCompatibility(compatibilityData));
            setError(null);
        } catch {
            setError("Could not load student details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { void refresh(); }, [studentId]);

    const instructorOptions = useMemo(
        () => instructors.map((instructor) => ({ value: instructor.instructor_id, label: instructor.name })),
        [instructors]
    );

    function openCompatibilityModal(instructorId = "") {
        setCompatibilityForm({
            ...emptyCompatibilityForm,
            instructor_id: instructorId,
        });
        setShowCompatibilityModal(true);
    }

    async function handleCompatibilitySubmit(e: React.FormEvent) {
        e.preventDefault();
        setSavingCompatibility(true);
        try {
            await addCompatibilityOverride({
                instructor_id: compatibilityForm.instructor_id,
                student_id: studentId,
                verdict: compatibilityForm.verdict,
                ...(compatibilityForm.reason.trim() && { reason: compatibilityForm.reason.trim() }),
                initiated_by: "admin",
            });
            setShowCompatibilityModal(false);
            await refresh();
        } catch {
            toast("Failed to save compatibility override.", "error");
        } finally {
            setSavingCompatibility(false);
        }
    }

    async function handleUpdateInstrumentSkillLevels(levels: InstrumentSkillLevel[]) {
        setSavingSkillLevels(true);
        try {
            const sanitized = levels.filter((isl) => isl.name.trim() && isl.family && isl.skill_level);
            await updateStudent(studentId, { instrument_skill_levels: sanitized });
            toast("Instrument skill levels updated.", "success");
            await refresh();
        } catch {
            toast("Failed to update instrument skill levels.", "error");
        } finally {
            setSavingSkillLevels(false);
        }
    }

    async function handleUpdateRequirements(requirements: TeachingRequirement[]) {
        setSavingRequirements(true);
        try {
            const sanitized = requirements
                .map((r) => ({ requirement_type: r.requirement_type, value: r.value.trim() }))
                .filter((r) => r.value.length > 0);
            await updateStudent(studentId, { requirements: sanitized });
            toast("Requirements updated.", "success");
            await refresh();
        } catch {
            toast("Failed to update requirements.", "error");
        } finally {
            setSavingRequirements(false);
        }
    }

    const blockedTimes = student?.blocked_times ?? [];

    function openBlockedTimeModal() {
        setBlockedTimeForm(emptyBlockedTimeForm);
        setShowBlockedTimeModal(true);
    }

    async function handleBlockedTimeSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!student) return;
        setSavingBlockedTime(true);
        try {
            const next = [...blockedTimes, toBlockedTimePayload(blockedTimeForm)];
            const updated = await updateStudentBlockedTimes(studentId, next);
            setStudent(updated);
            setShowBlockedTimeModal(false);
        } catch {
            toast("Failed to save blocked time.", "error");
        } finally {
            setSavingBlockedTime(false);
        }
    }

    async function handleBlockedTimeDelete(index: number) {
        if (!student) return;
        if (!confirm("Delete this blocked time?")) return;
        try {
            const next = blockedTimes.filter((_, i) => i !== index);
            const updated = await updateStudentBlockedTimes(studentId, next);
            setStudent(updated);
        } catch {
            toast("Failed to delete blocked time.", "error");
        }
    }

    return {
        student,
        enrollments,
        invoices,
        compatibility,
        loading,
        error,
        refresh,
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
    };
}
