"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { faDollarSign, faUserPlus, faFileInvoice } from "@fortawesome/free-solid-svg-icons";
import Button from "@/components/ui/button";
import DataState from "@/components/ui/data_state";
import Sections from "@/components/ui/sections";
import { useClientDetail } from "@/features/clients/hooks/use_client_detail";
import { useRecordPayment } from "@/features/clients/hooks/use_record_payment";
import { useAddClientStudent } from "@/features/clients/hooks/use_add_client_student";
import { useGenerateInvoice } from "@/features/clients/hooks/use_generate_invoice";
import ClientInfoCard from "@/features/clients/components/client_info_card";
import ClientStudentsTab from "@/features/clients/components/client_students_tab";
import ClientInvoicesTab from "@/features/clients/components/client_invoices_tab";
import ClientPaymentsTab from "@/features/clients/components/client_payments_tab";
import RecordPaymentModal from "@/features/clients/components/record_payment_modal";
import AddStudentModal from "@/features/clients/components/add_student_modal";
import GenerateInvoiceModal from "@/features/clients/components/generate_invoice_modal";

export default function ClientDetailPage() {
    const { clientId } = useParams() as { clientId: string };
    const router = useRouter();
    const { client, students, invoices, payments, loading, error, refresh } = useClientDetail(clientId);
    const { showPayModal, setShowPayModal, payAmount, setPayAmount, payMethod, setPayMethod, paying, handlePay } = useRecordPayment(clientId, refresh);
    const { showModal: showAddStudent, setShowModal: setShowAddStudent, form: studentForm, setForm: setStudentForm, saving: savingStudent, handleSubmit: handleAddStudent } = useAddClientStudent(clientId, refresh);
    const { showModal: showInvoiceModal, setShowModal: setShowInvoiceModal, openModal: openInvoiceModal, form: invoiceForm, setForm: setInvoiceForm, saving: savingInvoice, handleSubmit: handleGenerateInvoice } = useGenerateInvoice(students, refresh);
    const [activeSection, setActiveSection] = useState("students");

    return (
        <main className="page-client-detail">
            <DataState loading={loading} error={error} empty={!client} emptyMessage="Client not found.">
                <div className="page-header">
                    <div className="client-detail-back">
                        <Button variant="back" onClick={() => router.push("/clients")}>Clients</Button>
                        <h1>{client?.person.name}</h1>
                    </div>
                    <div className="page-header-actions">
                        <Button variant="primary"   icon={faDollarSign} onClick={() => setShowPayModal(true)}>Add Payment</Button>
                        <Button variant="secondary" icon={faUserPlus}   onClick={() => setShowAddStudent(true)}>Add Student</Button>
                        <Button variant="secondary" icon={faFileInvoice} onClick={openInvoiceModal}>Add Invoice</Button>
                    </div>
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
                {showAddStudent && (
                    <AddStudentModal
                        onClose={() => setShowAddStudent(false)}
                        onSubmit={handleAddStudent}
                        form={studentForm}
                        onChange={setStudentForm}
                        saving={savingStudent}
                    />
                )}
                {showInvoiceModal && (
                    <GenerateInvoiceModal
                        onClose={() => setShowInvoiceModal(false)}
                        onSubmit={handleGenerateInvoice}
                        form={invoiceForm}
                        onChange={setInvoiceForm}
                        students={students}
                        saving={savingInvoice}
                    />
                )}
            </DataState>
        </main>
    );
}
