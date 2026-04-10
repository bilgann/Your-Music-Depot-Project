import DataTable from "@/components/ui/data_table";
import type { ClientPayment } from "@/features/clients/api/client";

interface Props {
    payments: ClientPayment[];
}

export default function ClientPaymentsTab({ payments }: Props) {
    return (
        <DataTable
            loading={false}
            error={null}
            data={payments}
            emptyMessage="No payments recorded."
            getKey={(pay) => pay.transaction_id}
            columns={[
                { header: "Date", render: (pay) => pay.created_at?.slice(0, 10) || "--" },
                { header: "Amount", render: (pay) => `$${Number(pay.amount).toFixed(2)}` },
                { header: "Description", render: (pay) => pay.reason || "--" },
                { header: "Method", render: (pay) => pay.payment_method || "--" },
            ]}
        />
    );
}
