"use client"

import React, { useCallback, useEffect, useMemo, useState } from 'react'
import {
    getInvoiceLineItems,
    getInvoices,
    getOutstandingBalances,
    recordPayment,
    type Invoice,
    type InvoiceLineItem,
    type InvoiceStatus,
    type InvoiceSummary,
} from '../services/paymentService'

const defaultSummary: InvoiceSummary = {
    total_invoices: 0,
    pending: 0,
    paid: 0,
    cancelled: 0,
    outstanding_balance: 0,
}

function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency: 'CAD',
    }).format(amount)
}

function formatDate(value?: string): string {
    if (!value) return '-'
    const date = new Date(value)
    return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}

function lineItemTotal(item: InvoiceLineItem): number {
    if (typeof item.line_total === 'number') return item.line_total
    if (typeof item.amount === 'number') return item.amount
    return (item.quantity ?? 1) * (item.unit_price ?? 0)
}

export default function PaymentPage() {
    const [statusFilter, setStatusFilter] = useState<InvoiceStatus | 'All'>('All')
    const [invoices, setInvoices] = useState<Invoice[]>([])
    const [summary, setSummary] = useState<InvoiceSummary>(defaultSummary)
    const [outstandingTotal, setOutstandingTotal] = useState(0)
    const [selectedInvoiceId, setSelectedInvoiceId] = useState<number | null>(null)
    const [selectedLineItems, setSelectedLineItems] = useState<InvoiceLineItem[]>([])
    const [loading, setLoading] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const [paymentForm, setPaymentForm] = useState({
        invoice_id: '',
        amount: '',
        payment_method: 'Card',
        paid_on: new Date().toISOString().slice(0, 10),
        notes: '',
    })

    const selectedInvoice = useMemo(
        () => invoices.find((invoice) => invoice.invoice_id === selectedInvoiceId) ?? null,
        [invoices, selectedInvoiceId]
    )

    const loadInvoices = useCallback(async (filter: InvoiceStatus | 'All') => {
        const response = await getInvoices(filter === 'All' ? undefined : filter)
        setInvoices(response.data)
        setSummary(response.summary)

        if (!response.data.length) {
            setSelectedInvoiceId(null)
            setSelectedLineItems([])
            return
        }

        const invoiceExists = response.data.some((invoice) => invoice.invoice_id === selectedInvoiceId)
        const nextSelectedId = invoiceExists && selectedInvoiceId ? selectedInvoiceId : response.data[0].invoice_id
        setSelectedInvoiceId(nextSelectedId)

        const lines = await getInvoiceLineItems(nextSelectedId)
        setSelectedLineItems(lines)
    }, [selectedInvoiceId])

    const loadOutstandingBalance = useCallback(async () => {
        const response = await getOutstandingBalances()
        setOutstandingTotal(response.total_outstanding_balance)
    }, [])

    const refreshData = useCallback(async (filter: InvoiceStatus | 'All') => {
        setLoading(true)
        setError(null)
        try {
            await Promise.all([loadInvoices(filter), loadOutstandingBalance()])
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load payment data'
            setError(message)
        } finally {
            setLoading(false)
        }
    }, [loadInvoices, loadOutstandingBalance])

    useEffect(() => {
        void refreshData(statusFilter)
    }, [refreshData, statusFilter])

    async function handleSelectInvoice(invoiceId: number) {
        setSelectedInvoiceId(invoiceId)
        setPaymentForm((prev) => ({ ...prev, invoice_id: String(invoiceId) }))

        try {
            const lines = await getInvoiceLineItems(invoiceId)
            setSelectedLineItems(lines)
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load line items'
            setError(message)
            setSelectedLineItems([])
        }
    }

    async function handleSubmitPayment(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault()

        const invoiceId = Number(paymentForm.invoice_id)
        const amount = Number(paymentForm.amount)

        if (!invoiceId || !Number.isFinite(invoiceId)) {
            setError('Please select an invoice')
            return
        }

        if (!amount || amount <= 0) {
            setError('Payment amount must be greater than 0')
            return
        }

        setSubmitting(true)
        setError(null)
        try {
            await recordPayment({
                invoice_id: invoiceId,
                amount,
                payment_method: paymentForm.payment_method,
                paid_on: paymentForm.paid_on,
                notes: paymentForm.notes || undefined,
            })

            setPaymentForm((prev) => ({ ...prev, amount: '', notes: '' }))
            await refreshData(statusFilter)
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to record payment'
            setError(message)
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <main className="page-payments" style={{ padding: 20 }}>
            <h1>Payments</h1>

            <section style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 12, marginBottom: 16 }}>
                <article style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
                    <strong>Total Invoices</strong>
                    <p>{summary.total_invoices}</p>
                </article>
                <article style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
                    <strong>Pending</strong>
                    <p>{summary.pending}</p>
                </article>
                <article style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
                    <strong>Paid</strong>
                    <p>{summary.paid}</p>
                </article>
                <article style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
                    <strong>Outstanding Balance</strong>
                    <p>{formatCurrency(outstandingTotal || summary.outstanding_balance)}</p>
                </article>
            </section>

            <section style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
                {(['All', 'Pending', 'Paid', 'Cancelled'] as const).map((status) => (
                    <button
                        key={status}
                        onClick={() => setStatusFilter(status)}
                        disabled={statusFilter === status || loading}
                    >
                        {status}
                    </button>
                ))}
            </section>

            {error && (
                <p style={{ color: '#c0392b', marginBottom: 12 }} role="alert">
                    {error}
                </p>
            )}

            <section style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, alignItems: 'start' }}>
                <div style={{ border: '1px solid #ddd', borderRadius: 8, overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ background: '#f7f7f7' }}>
                                <th style={{ textAlign: 'left', padding: 10 }}>Invoice</th>
                                <th style={{ textAlign: 'left', padding: 10 }}>Student</th>
                                <th style={{ textAlign: 'left', padding: 10 }}>Status</th>
                                <th style={{ textAlign: 'right', padding: 10 }}>Outstanding</th>
                            </tr>
                        </thead>
                        <tbody>
                            {invoices.map((invoice) => (
                                <tr
                                    key={invoice.invoice_id}
                                    onClick={() => void handleSelectInvoice(invoice.invoice_id)}
                                    style={{
                                        cursor: 'pointer',
                                        background: selectedInvoiceId === invoice.invoice_id ? '#eef6ff' : 'transparent',
                                        borderTop: '1px solid #eee',
                                    }}
                                >
                                    <td style={{ padding: 10 }}>#{invoice.invoice_id}</td>
                                    <td style={{ padding: 10 }}>{invoice.student_name || '-'}</td>
                                    <td style={{ padding: 10 }}>{invoice.status}</td>
                                    <td style={{ textAlign: 'right', padding: 10 }}>{formatCurrency(invoice.outstanding_balance)}</td>
                                </tr>
                            ))}

                            {!loading && !invoices.length && (
                                <tr>
                                    <td colSpan={4} style={{ padding: 16, textAlign: 'center' }}>
                                        No invoices found for this filter.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>

                <aside style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
                    <h2 style={{ marginTop: 0 }}>Invoice Details</h2>

                    {!selectedInvoice && <p>Select an invoice to see line items.</p>}

                    {selectedInvoice && (
                        <>
                            <p>
                                <strong>Invoice:</strong> #{selectedInvoice.invoice_id}
                            </p>
                            <p>
                                <strong>Issued:</strong> {formatDate(selectedInvoice.issued_on)}
                            </p>
                            <p>
                                <strong>Due:</strong> {formatDate(selectedInvoice.due_on)}
                            </p>
                            <p>
                                <strong>Total:</strong> {formatCurrency(selectedInvoice.total_amount)}
                            </p>
                            <p>
                                <strong>Paid:</strong> {formatCurrency(selectedInvoice.amount_paid)}
                            </p>
                            <p>
                                <strong>Outstanding:</strong> {formatCurrency(selectedInvoice.outstanding_balance)}
                            </p>

                            <h3>Line Items</h3>
                            {!selectedLineItems.length && <p>No line items available.</p>}
                            <ul style={{ paddingLeft: 16 }}>
                                {selectedLineItems.map((item, index) => (
                                    <li key={`${selectedInvoice.invoice_id}-${index}`} style={{ marginBottom: 8 }}>
                                        <span>{item.description || `Item ${index + 1}`}</span>
                                        <span style={{ float: 'right' }}>{formatCurrency(lineItemTotal(item))}</span>
                                    </li>
                                ))}
                            </ul>
                        </>
                    )}
                </aside>
            </section>

            <section style={{ marginTop: 20, border: '1px solid #ddd', borderRadius: 8, padding: 16 }}>
                <h2 style={{ marginTop: 0 }}>Record Payment</h2>

                <form onSubmit={handleSubmitPayment} style={{ display: 'grid', gap: 10, maxWidth: 480 }}>
                    <label>
                        Invoice
                        <select
                            value={paymentForm.invoice_id}
                            onChange={(event) => setPaymentForm((prev) => ({ ...prev, invoice_id: event.target.value }))}
                            required
                        >
                            <option value="">Select invoice</option>
                            {invoices
                                .filter((invoice) => invoice.status === 'Pending' && invoice.outstanding_balance > 0)
                                .map((invoice) => (
                                    <option key={invoice.invoice_id} value={String(invoice.invoice_id)}>
                                        #{invoice.invoice_id} - {invoice.student_name} ({formatCurrency(invoice.outstanding_balance)})
                                    </option>
                                ))}
                        </select>
                    </label>

                    <label>
                        Amount
                        <input
                            type="number"
                            min="0.01"
                            step="0.01"
                            value={paymentForm.amount}
                            onChange={(event) => setPaymentForm((prev) => ({ ...prev, amount: event.target.value }))}
                            required
                        />
                    </label>

                    <label>
                        Payment Method
                        <select
                            value={paymentForm.payment_method}
                            onChange={(event) => setPaymentForm((prev) => ({ ...prev, payment_method: event.target.value }))}
                        >
                            <option value="Card">Card</option>
                            <option value="Cash">Cash</option>
                            <option value="E-Transfer">E-Transfer</option>
                            <option value="Bank Transfer">Bank Transfer</option>
                        </select>
                    </label>

                    <label>
                        Payment Date
                        <input
                            type="date"
                            value={paymentForm.paid_on}
                            onChange={(event) => setPaymentForm((prev) => ({ ...prev, paid_on: event.target.value }))}
                        />
                    </label>

                    <label>
                        Notes
                        <textarea
                            rows={3}
                            value={paymentForm.notes}
                            onChange={(event) => setPaymentForm((prev) => ({ ...prev, notes: event.target.value }))}
                            placeholder="Optional payment notes"
                        />
                    </label>

                    <button type="submit" disabled={submitting || loading}>
                        {submitting ? 'Saving Payment...' : 'Record Payment'}
                    </button>
                </form>
            </section>
        </main>
    )
}