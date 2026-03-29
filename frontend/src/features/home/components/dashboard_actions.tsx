import Button from "@/components/ui/button";
import { faPlus } from "@fortawesome/free-solid-svg-icons";

export default function DashboardActions() {
    return (
        <div className="dashboard-actions">
            <Button variant="action-primary" href="/students" icon={faPlus}>Add Student</Button>
        </div>
    );
}
