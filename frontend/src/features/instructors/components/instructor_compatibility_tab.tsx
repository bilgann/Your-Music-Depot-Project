import Pagination from "@/components/ui/pagination";
import { useClientPagination } from "@/hooks/use_client_pagination";
import type { InstructorCompatibility } from "@/features/instructors/api/instructor_detail";

interface Props {
    items: InstructorCompatibility[];
}

function getVerdictLabel(item: InstructorCompatibility) {
    return item.hard_verdict || item.soft_verdict || (item.can_assign ? "OK" : "Review Required");
}

function toClassName(verdict: string) {
    return verdict.toLowerCase().replace(/\s+/g, "-").replace(/_/g, "-");
}

export default function InstructorCompatibilityTab({ items }: Props) {
    const { page, pageCount, pageData, setPage } = useClientPagination(items);

    if (items.length === 0) {
        return <p className="table-empty">No current students are available to evaluate compatibility for this instructor.</p>;
    }

    return (
        <div>
            <p className="table-empty" style={{ marginBottom: 16 }}>
                This view shows live compatibility results for the instructor's current students. The backend does not expose saved override records by instructor yet.
            </p>
            <div className="data-table-wrapper">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Verdict</th>
                            <th>Reasons</th>
                        </tr>
                    </thead>
                    <tbody>
                        {pageData.map((item) => {
                            const verdict = getVerdictLabel(item);
                            return (
                                <tr key={item.student_id}>
                                    <td>{item.student_name}</td>
                                    <td>
                                        <span className={`status-badge status-${toClassName(verdict)}`}>
                                            {verdict}
                                        </span>
                                    </td>
                                    <td>{item.reasons.length ? item.reasons.join(", ") : "No issues detected."}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
            <Pagination page={page} pageCount={pageCount} onPageChange={setPage} />
        </div>
    );
}
