import { useMemo, useState } from "react";

const DEFAULT_PAGE_SIZE = 10;

export function useClientPagination<T>(items: T[], pageSize = DEFAULT_PAGE_SIZE) {
    const [page, setPage] = useState(1);

    const pageCount = Math.max(1, Math.ceil(items.length / pageSize));

    const safeSetPage = (next: number) => {
        setPage(Math.max(1, Math.min(next, pageCount)));
    };

    const pageData = useMemo(() => {
        const start = (page - 1) * pageSize;
        return items.slice(start, start + pageSize);
    }, [items, page, pageSize]);

    return { page, pageCount, pageData, setPage: safeSetPage };
}
