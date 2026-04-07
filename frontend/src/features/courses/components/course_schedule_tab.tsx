import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import type { CourseOccurrence } from "@/features/courses/api/course";

interface Props {
    occurrences: CourseOccurrence[];
    projecting: boolean;
    onProject: () => void;
}

export default function CourseScheduleTab({ occurrences, projecting, onProject }: Props) {
    return (
        <>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <p className="table-empty" style={{ margin: 0 }}>
                    Existing projected occurrences are not exposed by the backend yet. Use project to refresh the schedule in this session.
                </p>
                <Button variant="primary" onClick={onProject} disabled={projecting}>
                    {projecting ? "Projecting..." : "Project Schedule"}
                </Button>
            </div>
            <DataTable
                loading={false}
                error={null}
                data={occurrences}
                emptyMessage="No projected occurrences yet. Project the course schedule to generate them."
                getKey={(occurrence) => occurrence.occurrence_id}
                columns={[
                    { header: "Date", render: (occurrence) => occurrence.date },
                    { header: "Start", render: (occurrence) => occurrence.start_time },
                    { header: "End", render: (occurrence) => occurrence.end_time },
                    { header: "Status", render: (occurrence) => occurrence.status },
                ]}
            />
        </>
    );
}