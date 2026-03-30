import { useEffect, useMemo, useState } from "react";
import { getInstructors } from "@/features/instructors/api/instructor";
import { addCompatibilityOverride, checkCompatibility } from "@/features/students/api/compatibility";
import { getStudentById, getStudentLessons, getStudentInvoices } from "@/features/students/api/student";
import { useToast } from "@/components/ui/toast";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { StudentCompatibilityItem } from "@/features/students/api/compatibility";
import type { Student, StudentEnrollment, StudentInvoice } from "@/features/students/api/student";

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

    return {
        student,
        enrollments,
        invoices,
        compatibility,
        loading,
        error,
        refresh,
        showCompatibilityModal,
        setShowCompatibilityModal,
        compatibilityForm,
        setCompatibilityForm,
        savingCompatibility,
        instructorOptions,
        openCompatibilityModal,
        handleCompatibilitySubmit,
    };
}
