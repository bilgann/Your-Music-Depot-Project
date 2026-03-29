import { useState, useEffect } from "react";
import { getInstructors } from "@/features/instructors/api/instructor";
import type { Instructor } from "@/features/instructors/api/instructor";

export function useInstructors() {
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            setInstructors(await getInstructors());
            setError(null);
        } catch {
            setError("Could not load instructors.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { refresh(); }, []);

    return { instructors, loading, error, refresh };
}
