"use client";

import Navbar from "@/components/ui/navbar";
import { useDashboard } from "@/features/home/hooks/use_dashboard";
import DashboardStats from "@/features/home/components/dashboard_stats";
import DashboardActions from "@/features/home/components/dashboard_actions";
import LessonCalendar from "@/features/scheduling/components/lesson_calendar";

export default function HomePage() {
    const { todayCount, nextLesson, loading, error } = useDashboard();

    return (
        <>
            <Navbar title="Dashboard" className="page-home" />
            <div className="dashboard-content">
                {error && <p className="dashboard-error">{error}</p>}
                <DashboardStats loading={loading} todayCount={todayCount} nextLesson={nextLesson} />
                <DashboardActions />
            </div>
            <LessonCalendar onLessonCreated={() => {}} />
        </>
    );
}
