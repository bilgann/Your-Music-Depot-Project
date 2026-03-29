interface Props {
    loading: boolean;
    todayCount: number | null;
    nextLesson: { start_time: string } | null;
}

export default function DashboardStats({ loading, todayCount, nextLesson }: Props) {
    function formatTime(iso: string) {
        return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    }

    function formatDate(iso: string) {
        return new Date(iso).toLocaleDateString([], { weekday: "short", month: "short", day: "numeric" });
    }

    return (
        <div className="dashboard-stats">
            <div className="stat-card">
                <span className="stat-label">Today&apos;s Lessons</span>
                <span className="stat-value">{loading ? "—" : todayCount}</span>
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
    );
}
