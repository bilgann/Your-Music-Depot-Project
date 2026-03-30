import InfoCard from "@/components/ui/info_card";
import DataTable from "@/components/ui/data_table";
import type { Invoice, InvoiceLineItem } from "@/features/invoices/api/invoice";

interface Props {
    invoice: Invoice;
    studentName: string;
    lineItems: InvoiceLineItem[];
}

function formatAmount(amount: number) {
    return `$${Number(amount).toFixed(2)}`;
}

export default function InvoiceDetail({ invoice, studentName, lineItems }: Props) {
    return (
        <>
            <InfoCard
                rows={[
                    { label: "Client", value: invoice.client?.person?.name ?? "--" },
                    { label: "Student", value: studentName },
                    { label: "Status", value: invoice.status },
                    { label: "Total", value: formatAmount(invoice.total_amount) },
                    { label: "Paid", value: formatAmount(invoice.amount_paid) },
                    { label: "Period", value: `${invoice.period_start} to ${invoice.period_end}` },
                ]}
            />
            <DataTable
                loading={false}
                error={null}
                data={lineItems}
                emptyMessage="No line items found for this invoice."
                getKey={(item) => item.line_id}
                columns={[
                    { header: "Description", render: (item) => item.description },
                    { header: "Item Type", render: (item) => item.item_type ?? "lesson" },
                    { header: "Attendance", render: (item) => item.attendance_status || "--" },
                    { header: "Amount", render: (item) => formatAmount(item.amount) },
                ]}
            />
        </>
    );
}