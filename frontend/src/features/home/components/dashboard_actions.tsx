import Link from "next/link";

export default function DashboardActions() {
    return (
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
    );
}
