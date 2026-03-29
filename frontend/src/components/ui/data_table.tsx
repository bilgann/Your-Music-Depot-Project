import { faPencil, faTrash, faChevronLeft, faChevronRight } from "@fortawesome/free-solid-svg-icons";
import Button from "./button";
import DataState from "./data_state";

export interface Column<T> {
    header: string;
    render: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
    loading: boolean;
    error: string | null;
    data: T[];
    emptyMessage?: string;
    columns: Column<T>[];
    getKey: (row: T) => string | number;
    onEdit?: (row: T) => void;
    onDelete?: (row: T) => void;
    onRowClick?: (row: T) => void;
    page?: number;
    pageCount?: number;
    onPageChange?: (page: number) => void;
}

export default function DataTable<T>({
    loading,
    error,
    data,
    emptyMessage,
    columns,
    getKey,
    onEdit,
    onDelete,
    onRowClick,
    page,
    pageCount,
    onPageChange,
}: DataTableProps<T>) {
    const hasActions = onEdit || onDelete;
    const paginationEnabled = !!onPageChange && page !== undefined && pageCount !== undefined;
    const currentPage  = page      ?? 1;
    const currentCount = pageCount ?? 1;

    return (
        <>
            <DataState loading={loading} error={error} empty={data.length === 0} emptyMessage={emptyMessage}>
                <div className="data-table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                {columns.map((col) => (
                                    <th key={col.header}>{col.header}</th>
                                ))}
                                {hasActions && <th>Actions</th>}
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row) => (
                                <tr
                                    key={getKey(row)}
                                    onClick={onRowClick ? () => onRowClick(row) : undefined}
                                    style={onRowClick ? { cursor: "pointer" } : undefined}
                                >
                                    {columns.map((col) => (
                                        <td key={col.header}>{col.render(row)}</td>
                                    ))}
                                    {hasActions && (
                                        <td>
                                            <div
                                                className="actions-cell"
                                                onClick={onRowClick ? (e) => e.stopPropagation() : undefined}
                                            >
                                                {onEdit && (
                                                    <Button variant="icon" onClick={() => onEdit(row)} title="Edit" icon={faPencil} />
                                                )}
                                                {onDelete && (
                                                    <Button variant="icon-danger" onClick={() => onDelete(row)} title="Delete" icon={faTrash} />
                                                )}
                                            </div>
                                        </td>
                                    )}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </DataState>

            <div className="pagination">
                <Button
                    variant="icon"
                    icon={faChevronLeft}
                    onClick={paginationEnabled ? () => onPageChange(currentPage - 1) : undefined}
                    disabled={!paginationEnabled || currentPage <= 1}
                    title="Previous page"
                />
                <span className="pagination-info">
                    {paginationEnabled ? `Page ${currentPage} of ${currentCount}` : "—"}
                </span>
                <Button
                    variant="icon"
                    icon={faChevronRight}
                    onClick={paginationEnabled ? () => onPageChange(currentPage + 1) : undefined}
                    disabled={!paginationEnabled || currentPage >= currentCount}
                    title="Next page"
                />
            </div>
        </>
    );
}
