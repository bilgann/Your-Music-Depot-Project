import { useCallback, useEffect, useMemo, useState } from "react";
import { listInvoices } from "@/features/invoices/api/invoice";
import { getStudents } from "@/features/students/api/student";
import type { Invoice } from "@/features/invoices/api/invoice";
import type { Student } from "@/features/students/api/student";

const PAGE_SIZE = 20;

export function useInvoices() {
    const [allInvoices, setAllInvoices] = useState<Invoice[]>([]);
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [page, setPage] = useState(1);
    const [search, setSearchRaw] = useState("");

    const studentNameById = useMemo(
        () => Object.fromEntries(students.map((student) => [student.student_id, student.person.name])),
        [students]
    );

    const filteredInvoices = useMemo(() => {
        const query = search.trim().toLowerCase();
        if (!query) return allInvoices;

        return allInvoices.filter((invoice) => {
            const clientName = invoice.client?.person?.name ?? "";
            const studentName = invoice.student_id ? (studentNameById[invoice.student_id] ?? "") : "";
            const haystack = [
                invoice.invoice_id,
                clientName,
                studentName,
                invoice.status,
                invoice.period_start,
                invoice.period_end,
            ].join(" ").toLowerCase();
            return haystack.includes(query);
        });
    }, [allInvoices, search, studentNameById]);

    const total = filteredInvoices.length;
    const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

    const invoices = useMemo(() => {
        const startIndex = (page - 1) * PAGE_SIZE;
        return filteredInvoices.slice(startIndex, startIndex + PAGE_SIZE);
    }, [filteredInvoices, page]);

    const refresh = useCallback(async () => {
        try {
            setLoading(true);
            const [invoiceData, studentData] = await Promise.all([
                listInvoices(),
                getStudents(),
            ]);
            setAllInvoices(invoiceData);
            setStudents(studentData);
            setError(null);
        } catch {
            setError("Could not load invoices.");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { void refresh(); }, [refresh]);

    useEffect(() => {
        if (page > pageCount) {
            setPage(pageCount);
        }
    }, [page, pageCount]);

    function setSearch(searchValue: string) {
        setSearchRaw(searchValue);
        setPage(1);
    }

    return { invoices, students, loading, error, refresh, page, setPage, search, setSearch, pageCount };
}