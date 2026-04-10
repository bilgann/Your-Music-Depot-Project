import { faChevronLeft, faChevronRight } from "@fortawesome/free-solid-svg-icons";
import Button from "./button";

interface Props {
    page: number;
    pageCount: number;
    onPageChange: (page: number) => void;
}

export default function Pagination({ page, pageCount, onPageChange }: Props) {
    if (pageCount <= 1) return null;

    return (
        <div className="pagination">
            <Button
                variant="icon"
                icon={faChevronLeft}
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
                title="Previous page"
            />
            <span className="pagination-info">Page {page} of {pageCount}</span>
            <Button
                variant="icon"
                icon={faChevronRight}
                onClick={() => onPageChange(page + 1)}
                disabled={page >= pageCount}
                title="Next page"
            />
        </div>
    );
}
