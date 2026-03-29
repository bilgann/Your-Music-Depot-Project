import { useState, useEffect } from "react";
import { getLessons } from "@/features/home/api/dashboard";
import type { Lesson } from "@/types/index";

export function useDashboard() {
    const [todayCount, setTodayCount] = useState<number | null>(null);
    const [nextLesson, setNextLesson] = useState<Lesson | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function fetch() {
            try {
                const lessons = await getLessons();
                const now = new Date();
                const todayStr = now.toISOString().slice(0, 10);
                setTodayCount(lessons.filter((l) => l.start_time?.startsWith(todayStr)).length);
                const upcoming = lessons
                    .filter((l) => new Date(l.start_time) > now)
                    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
                setNextLesson(upcoming[0] ?? null);
                setError(null);
            } catch {
                setError("Could not load lesson data.");
            } finally {
                setLoading(false);
            }
        }
        fetch();
    }, []);

    return { todayCount, nextLesson, loading, error };
}
