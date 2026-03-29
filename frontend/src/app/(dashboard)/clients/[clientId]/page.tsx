"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import DataState from "@/components/ui/data_state";
import Sections from "@/components/ui/sections";
import { useClientDetail } from "@/features/clients/hooks/use_client_detail";
import { useRecordPayment } from "@/features/clients/hooks/use_record_payment";
import ClientInfoCard from "@/features/clients/components/client_info_card";
import ClientStudentsTab from "@/features/clients/components/client_students_tab";
import ClientInvoicesTab from "@/features/clients/components/client_invoices_tab";
import ClientPaymentsTab from "@/features/clients/components/client_payments_tab";
import RecordPaymentModal from "@/features/clients/components/record_payment_modal";

export default function ClientDetailPage() {
    const { clientId } = useParams() as { clientId: string };
    const router = useRouter();
    const { client, students, invoices, payments, loading, error, refresh } = useClientDetail(clientId);
    const { showPayModal, setShowPayModal, payAmount, setPayAmount, payMethod, setPayMethod, paying, handlePay } = useRecordPayment(clientId, refresh);
    const [activeSection, setActiveSection] = useState("students");

    return (
        <main className="page-client-detail">
            <DataState loading={loading} error={error} empty={!client} emptyMessage="Client not found.">
                <div className="page-header">
                    <div className="client-detail-back">
                        <button className="btn-back" onClick={() => router.push("/clients")}>&#8592; Clients</button>
                        <h1>{client?.person.name}</h1>
                    </div>
                    <button className="btn btn-primary" onClick={() => setShowPayModal(true)}>+ Record Payment</button>
                </div>

                <ClientInfoCard client={client!} />

                <Sections
                    active={activeSection}
                    onChange={setActiveSection}
                    sections={[
                        { key: "students", label: "Students", content: <ClientStudentsTab students={students} /> },
                        { key: "invoices", label: "Invoices", content: <ClientInvoicesTab invoices={invoices} /> },
                        { key: "payments", label: "Payments", content: <ClientPaymentsTab payments={payments} /> },
                    ]}
                />

                {showPayModal && (
                    <RecordPaymentModal
                        onClose={() => setShowPayModal(false)}
                        onSubmit={handlePay}
                        amount={payAmount}
                        onAmountChange={setPayAmount}
                        method={payMethod}
                        onMethodChange={setPayMethod}
                        saving={paying}
                    />
                )}
            </DataState>
        </main>
    );
}
