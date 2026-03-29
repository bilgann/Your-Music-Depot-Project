import { useState, useEffect } from "react";
import { getStudents } from "@/features/students/api/student";
import type { Student } from "@/features/students/api/student";

export function useStudents() {
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            setStudents(await getStudents());
            setError(null);
        } catch {
            setError("Could not load students.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, []);

    return { students, loading, error, refresh };
}
