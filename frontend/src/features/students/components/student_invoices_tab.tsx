import type { StudentInvoice } from "@/features/students/api/student";

interface Props {
    invoices: StudentInvoice[];
}

export default function StudentInvoicesTab({ invoices }: Props) {
    if (invoices.length === 0) {
        return <p className="table-empty">No invoices found.</p>;
    }
    return (
        <div className="data-table-wrapper">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Period</th>
                        <th>Total</th>
                        <th>Paid</th>
                        <th>Balance</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {invoices.map((inv) => (
                        <tr key={inv.invoice_id}>
                            <td>{inv.period_start} – {inv.period_end}</td>
                            <td>${Number(inv.total_amount).toFixed(2)}</td>
                            <td>${Number(inv.amount_paid).toFixed(2)}</td>
                            <td>${(Number(inv.total_amount) - Number(inv.amount_paid)).toFixed(2)}</td>
                            <td>
                                <span className={`status-badge status-${inv.status.toLowerCase().replace(" ", "-")}`}>
                                    {inv.status}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
