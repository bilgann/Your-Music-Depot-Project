import { useState, useEffect } from "react";
import { getStudentById, getStudentLessons, getStudentInvoices } from "@/features/students/api/student";
import type { Student, StudentEnrollment, StudentInvoice } from "@/features/students/api/student";

export function useStudentDetail(studentId: string) {
    const [student, setStudent] = useState<Student | null>(null);
    const [enrollments, setEnrollments] = useState<StudentEnrollment[]>([]);
    const [invoices, setInvoices] = useState<StudentInvoice[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            const [studentData, lessonsData, invoicesData] = await Promise.all([
                getStudentById(studentId),
                getStudentLessons(studentId),
                getStudentInvoices(studentId),
            ]);
            setStudent(studentData);
            setEnrollments(lessonsData);
            setInvoices(invoicesData);
            setError(null);
        } catch {
            setError("Could not load student details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, [studentId]);

    return { student, enrollments, invoices, loading, error, refresh };
}
