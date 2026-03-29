interface DataStateProps {
    loading: boolean;
    error: string | null;
    empty: boolean;
    emptyMessage?: string;
    children: React.ReactNode;
}

export default function DataState({
    loading,
    error,
    empty,
    emptyMessage = "No records found.",
    children,
}: DataStateProps) {
    if (loading) return <p className="table-loading">Loading...</p>;
    if (error)   return <p className="table-error">{error}</p>;
    if (empty)   return <p className="table-empty">{emptyMessage}</p>;
    return <>{children}</>;
}
