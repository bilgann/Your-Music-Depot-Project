"use client";

import { useDashboard } from "@/features/home/hooks/use_dashboard";
import DashboardStats from "@/features/home/components/dashboard_stats";
import DashboardActions from "@/features/home/components/dashboard_actions";

export default function HomePage() {
    const { todayCount, nextLesson, loading, error } = useDashboard();

    return (
        <div className="dashboard-page">
            <h1 className="dashboard-title">Dashboard</h1>
            {error && <p className="dashboard-error">{error}</p>}
            <DashboardStats loading={loading} todayCount={todayCount} nextLesson={nextLesson} />
            <DashboardActions />
        </div>
    );
}
