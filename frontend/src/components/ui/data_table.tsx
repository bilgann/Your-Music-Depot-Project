import { faPencil, faTrash } from "@fortawesome/free-solid-svg-icons";
import Button from "./button";
import DataState from "./data_state";
import Pagination from "./pagination";
import { useClientPagination } from "@/hooks/use_client_pagination";

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
    clientPageSize?: number;
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
    page: externalPage,
    pageCount: externalPageCount,
    onPageChange: externalOnPageChange,
    clientPageSize = 10,
}: DataTableProps<T>) {
    const hasActions = onEdit || onDelete;
    const serverPaginated = !!externalOnPageChange && externalPage !== undefined && externalPageCount !== undefined;

    const clientPagination = useClientPagination(data, clientPageSize);

    const rows = serverPaginated ? data : clientPagination.pageData;
    const page = serverPaginated ? externalPage : clientPagination.page;
    const pageCount = serverPaginated ? externalPageCount : clientPagination.pageCount;
    const onPageChange = serverPaginated ? externalOnPageChange : clientPagination.setPage;

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
                            {rows.map((row) => (
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

            <Pagination page={page} pageCount={pageCount} onPageChange={onPageChange} />
        </>
    );
}
