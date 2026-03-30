import Button from "@/components/ui/button";
import Pagination from "@/components/ui/pagination";
import { useClientPagination } from "@/hooks/use_client_pagination";
import type { StudentCompatibilityItem } from "@/features/students/api/compatibility";

interface Props {
    items: StudentCompatibilityItem[];
    onAddOverride: () => void;
    onEditOverride: (instructorId: string) => void;
}

function getVerdictLabel(item: StudentCompatibilityItem) {
    if (!item.can_assign) return "Blocked";
    if (item.hard_verdict === "required") return "Required";
    if (item.soft_verdict === "preferred") return "Preferred";
    if (item.soft_verdict === "disliked") return "Disliked";
    return "OK";
}

function getVerdictClassName(item: StudentCompatibilityItem) {
    if (!item.can_assign) return "blocked";
    if (item.hard_verdict === "required") return "required";
    if (item.soft_verdict === "preferred") return "preferred";
    if (item.soft_verdict === "disliked") return "disliked";
    return "present";
}

export default function StudentCompatibilityTab({ items, onAddOverride, onEditOverride }: Props) {
    const { page, pageCount, pageData, setPage } = useClientPagination(items);

    return (
        <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, marginBottom: 16 }}>
                <p className="table-empty" style={{ margin: 0 }}>
                    This view shows live compatibility checks across all instructors. Pair overrides can be saved here, but the backend does not expose override IDs for standalone delete actions yet.
                </p>
                <Button variant="primary" onClick={onAddOverride}>Add Override</Button>
            </div>

            {items.length === 0 ? (
                <p className="table-empty">No instructors available to evaluate compatibility.</p>
            ) : (
                <>
                    <div className="data-table-wrapper">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Instructor</th>
                                    <th>Verdict</th>
                                    <th>Reasons</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pageData.map((item) => (
                                    <tr key={item.instructor_id}>
                                        <td>{item.instructor_name}</td>
                                        <td>
                                            <span className={`status-badge status-${getVerdictClassName(item)}`}>
                                                {getVerdictLabel(item)}
                                            </span>
                                        </td>
                                        <td>{item.reasons.length > 0 ? item.reasons.join(" ") : "No compatibility warnings."}</td>
                                        <td>
                                            <Button variant="secondary" onClick={() => onEditOverride(item.instructor_id)}>
                                                Save Override
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <Pagination page={page} pageCount={pageCount} onPageChange={setPage} />
                </>
            )}
        </div>
    );
}
