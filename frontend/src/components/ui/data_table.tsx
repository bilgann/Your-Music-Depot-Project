import { faPencil, faTrash } from "@fortawesome/free-solid-svg-icons";
import Button from "./button";
import DataState from "./data_state";

export interface Column<T> {
    header: string;
    render: (row: T) => React.ReactNode;
}

interface DataTableProps<T> {
    title: string;
    addLabel?: string;
    onAdd?: () => void;
    loading: boolean;
    error: string | null;
    data: T[];
    emptyMessage?: string;
    columns: Column<T>[];
    getKey: (row: T) => string | number;
    onEdit?: (row: T) => void;
    onDelete?: (row: T) => void;
    onRowClick?: (row: T) => void;
}

export default function DataTable<T>({
    title,
    addLabel,
    onAdd,
    loading,
    error,
    data,
    emptyMessage,
    columns,
    getKey,
    onEdit,
    onDelete,
    onRowClick,
}: DataTableProps<T>) {
    const hasActions = onEdit || onDelete;

    return (
        <>
            <div className="page-header">
                <h1>{title}</h1>
                {onAdd && (
                    <Button variant="primary" onClick={onAdd}>
                        {addLabel ?? `+ Add ${title.replace(/s$/, "")}`}
                    </Button>
                )}
            </div>

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
        </>
    );
}
