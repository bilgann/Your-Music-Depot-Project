import { useEffect, useMemo, useState } from "react";
import { getStudents } from "@/features/students/api/student";
import { getInvoiceById, getInvoiceLineItems } from "@/features/invoices/api/invoice";
import type { Invoice, InvoiceLineItem } from "@/features/invoices/api/invoice";
import type { Student } from "@/features/students/api/student";

export function useInvoiceDetail(invoiceId: string) {
    const [invoice, setInvoice] = useState<Invoice | null>(null);
    const [lineItems, setLineItems] = useState<InvoiceLineItem[]>([]);
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    async function refresh() {
        try {
            setLoading(true);
            const [invoiceData, lineItemData, studentData] = await Promise.all([
                getInvoiceById(invoiceId),
                getInvoiceLineItems(invoiceId),
                getStudents(),
            ]);
            setInvoice(invoiceData);
            setLineItems(lineItemData);
            setStudents(studentData);
            setError(null);
        } catch {
            setError("Could not load invoice details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { void refresh(); }, [invoiceId]);

    const studentName = useMemo(() => {
        if (!invoice?.student_id) return "--";
        return students.find((student) => student.student_id === invoice.student_id)?.person.name ?? invoice.student_id;
    }, [invoice, students]);

    return { invoice, lineItems, studentName, loading, error, refresh };
}