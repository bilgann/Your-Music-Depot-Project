"use client";

import { useRouter } from "next/navigation";
import Navbar from "@/components/ui/navbar";
import DataTable from "@/components/ui/data_table";
import { useInvoices } from "@/features/invoices/hooks/use_invoices";
import type { Invoice } from "@/features/invoices/api/invoice";

function formatMoney(amount: number) {
    return `$${Number(amount).toFixed(2)}`;
}

function formatDate(value?: string | null) {
    if (!value) return "--";
    return new Date(value).toLocaleDateString([], { year: "numeric", month: "short", day: "numeric" });
}

export default function InvoicesPage() {
    const router = useRouter();
    const { invoices, students, loading, error, page, setPage, search, setSearch, pageCount } = useInvoices();

    function getStudentName(invoice: Invoice) {
        if (!invoice.student_id) return "--";
        return students.find((student) => student.student_id === invoice.student_id)?.person.name ?? invoice.student_id;
    }

    return (
        <>
            <Navbar
                title="Invoices"
                className="page-invoices"
                search={search}
                onSearchChange={setSearch}
            />
            <DataTable
                loading={loading}
                error={error}
                data={invoices}
                emptyMessage="No invoices found."
                getKey={(invoice) => invoice.invoice_id}
                columns={[
                    { header: "Client", render: (invoice) => invoice.client?.person?.name ?? "--" },
                    { header: "Student", render: (invoice) => getStudentName(invoice) },
                    { header: "Status", render: (invoice) => invoice.status },
                    { header: "Total", render: (invoice) => formatMoney(invoice.total_amount) },
                    { header: "Created", render: (invoice) => formatDate(invoice.created_at ?? invoice.period_start) },
                ]}
                onRowClick={(invoice) => router.push(`/invoices/${invoice.invoice_id}`)}
                page={page}
                pageCount={pageCount}
                onPageChange={setPage}
            />
        </>
    );
}