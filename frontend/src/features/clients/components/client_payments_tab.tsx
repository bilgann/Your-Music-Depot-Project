import type { ClientPayment } from "@/features/clients/api/client";

interface Props {
    payments: ClientPayment[];
}

export default function ClientPaymentsTab({ payments }: Props) {
    if (payments.length === 0) {
        return <p className="table-empty">No payments recorded.</p>;
    }
    return (
        <div className="data-table-wrapper">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Amount</th>
                        <th>Method</th>
                        <th>Invoice</th>
                    </tr>
                </thead>
                <tbody>
                    {payments.map((pay) => (
                        <tr key={pay.payment_id}>
                            <td>{pay.paid_on?.slice(0, 10) || "--"}</td>
                            <td>${Number(pay.amount).toFixed(2)}</td>
                            <td>{pay.payment_method || "--"}</td>
                            <td>{pay.invoice_id}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
