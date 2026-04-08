import DataTable from "@/components/ui/data_table";
import type { StudentInvoice } from "@/features/students/api/student";

interface Props {
    invoices: StudentInvoice[];
}

export default function StudentInvoicesTab({ invoices }: Props) {
    return (
        <DataTable
            loading={false}
            error={null}
            data={invoices}
            emptyMessage="No invoices found."
            getKey={(inv) => inv.invoice_id}
            columns={[
                { header: "Period", render: (inv) => `${inv.period_start} – ${inv.period_end}` },
                { header: "Total", render: (inv) => `$${Number(inv.total_amount).toFixed(2)}` },
                { header: "Paid", render: (inv) => `$${Number(inv.amount_paid).toFixed(2)}` },
                { header: "Balance", render: (inv) => `$${(Number(inv.total_amount) - Number(inv.amount_paid)).toFixed(2)}` },
                {
                    header: "Status",
                    render: (inv) => (
                        <span className={`status-badge status-${inv.status.toLowerCase().replace(" ", "-")}`}>
                            {inv.status}
                        </span>
                    ),
                },
            ]}
        />
    );
}
