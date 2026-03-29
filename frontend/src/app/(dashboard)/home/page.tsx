"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import config from "@/config";

type Lesson = {
    lesson_id: number;
    start_time: string;
    end_time: string;
    status: string;
    instructor_id?: number;
    student_id?: number;
    room_id?: number;
};

export default function HomePage() {
    const router = useRouter();
    const [todayCount, setTodayCount] = useState<number | null>(null);
    const [nextLesson, setNextLesson] = useState<Lesson | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // const token = localStorage.getItem("token");
        // if (!token) {
        //     router.replace("/login");
        //     return;
        // }

        async function fetchLessons() {
            try {
                const res = await fetch(`${config.API_BASE}/api/lessons`, {
                    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
                });
                if (!res.ok) throw new Error("Failed to load lessons.");
                const body = await res.json();
                const lessons: Lesson[] = body.data ?? [];

                const now = new Date();
                const todayStr = now.toISOString().slice(0, 10);

                const todayLessons = lessons.filter((l) =>
                    l.start_time?.startsWith(todayStr)
                );
                setTodayCount(todayLessons.length);

                const upcoming = lessons
                    .filter((l) => new Date(l.start_time) > now)
                    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
                setNextLesson(upcoming[0] ?? null);
            } catch (e) {
                setError("Could not load lesson data.");
            } finally {
                setLoading(false);
            }
        }

        fetchLessons();
    }, [router]);

    function formatTime(iso: string) {
        return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    function formatDate(iso: string) {
        return new Date(iso).toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
    }

    return (
        <div className="dashboard-page">
            <h1 className="dashboard-title">Dashboard</h1>

            {error && <p className="dashboard-error">{error}</p>}

            <div className="dashboard-stats">
                <div className="stat-card">
                    <span className="stat-label">Today&apos;s Lessons</span>
                    <span className="stat-value">
                        {loading ? "—" : todayCount}
                    </span>
                </div>

                <div className="stat-card">
                    <span className="stat-label">Next Lesson</span>
                    {loading ? (
                        <span className="stat-value">—</span>
                    ) : nextLesson ? (
                        <div className="stat-next">
                            <span className="stat-value">{formatTime(nextLesson.start_time)}</span>
                            <span className="stat-sub">{formatDate(nextLesson.start_time)}</span>
                        </div>
                    ) : (
                        <span className="stat-value stat-empty">None scheduled</span>
                    )}
                </div>
            </div>

            <div className="dashboard-actions">
                <Link href="/schedule" className="action-btn action-btn--primary">
                    + Add Lesson
                </Link>
                <Link href="/students" className="action-btn action-btn--secondary">
                    + Add Student
                </Link>
                <Link href="/schedule" className="action-btn action-btn--ghost">
                    View Schedule
                </Link>
            </div>
        </div>
    );
}
