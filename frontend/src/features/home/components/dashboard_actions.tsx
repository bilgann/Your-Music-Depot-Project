import Button from "@/components/ui/button";
import { faPlus, faCalendar } from "@fortawesome/free-solid-svg-icons";

export default function DashboardActions() {
    return (
        <div className="dashboard-actions">
            <Button variant="action-primary"   href="/schedule" icon={faPlus}>Add Lesson</Button>
            <Button variant="action-secondary" href="/students" icon={faPlus}>Add Student</Button>
            <Button variant="action-ghost"     href="/schedule" icon={faCalendar}>View Schedule</Button>
        </div>
    );
}
