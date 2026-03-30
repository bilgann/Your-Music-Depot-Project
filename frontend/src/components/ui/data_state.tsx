interface DataStateProps {
    loading: boolean;
    error: string | null;
    empty: boolean;
    emptyMessage?: string;
    children: React.ReactNode;
}

function Skeleton() {
    return (
        <div className="skeleton-wrapper">
            <div className="skeleton-line skeleton-line--long" />
            <div className="skeleton-line skeleton-line--medium" />
            <div className="skeleton-line skeleton-line--short" />
            <div className="skeleton-line skeleton-line--long" />
            <div className="skeleton-line skeleton-line--medium" />
        </div>
    );
}

export default function DataState({
    loading,
    error,
    empty,
    emptyMessage = "No records found.",
    children,
}: DataStateProps) {
    if (loading) return <Skeleton />;
    if (error)   return <p className="table-error">{error}</p>;
    if (empty)   return <p className="table-empty">{emptyMessage}</p>;
    return <>{children}</>;
}
