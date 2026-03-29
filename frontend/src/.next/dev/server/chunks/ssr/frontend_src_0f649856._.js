module.exports = [
"[project]/frontend/src/config.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>__TURBOPACK__default__export__
]);
const config = {
    API_BASE: process.env.REACT_APP_API_BASE || 'http://localhost:5000/api'
};
const __TURBOPACK__default__export__ = config;
}),
"[project]/frontend/src/services/paymentService.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "getInvoiceLineItems",
    ()=>getInvoiceLineItems,
    "getInvoices",
    ()=>getInvoices,
    "getOutstandingBalances",
    ()=>getOutstandingBalances,
    "recordPayment",
    ()=>recordPayment
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/src/config.ts [app-ssr] (ecmascript)");
;
function extractErrorMessage(raw) {
    if (typeof raw === 'string' && raw.trim()) return raw;
    if (raw && typeof raw === 'object') {
        const obj = raw;
        if (typeof obj.error === 'string' && obj.error) return obj.error;
        if (typeof obj.message === 'string' && obj.message) return obj.message;
        if (typeof obj.details === 'string' && obj.details) return obj.details;
    }
    return 'Request failed';
}
async function parseError(res) {
    try {
        const data = await res.json();
        throw new Error(extractErrorMessage(data));
    } catch  {
        const text = await res.text();
        throw new Error(extractErrorMessage(text) || `Request failed: ${res.status}`);
    }
}
function toNumber(value) {
    const asNumber = Number(value);
    return Number.isFinite(asNumber) ? asNumber : 0;
}
function normalizeInvoiceStatus(value) {
    const normalized = String(value ?? '').trim().toLowerCase();
    if (normalized === 'paid') return 'Paid';
    if (normalized === 'cancelled' || normalized === 'canceled') return 'Cancelled';
    return 'Pending';
}
function normalizeInvoice(raw) {
    const record = raw ?? {};
    return {
        invoice_id: toNumber(record.invoice_id ?? record.id),
        student_id: toNumber(record.student_id ?? record.customer_id) || undefined,
        student_name: String(record.student_name ?? record.customer_name ?? record.full_name ?? 'Unknown Student'),
        issued_on: typeof record.issued_on === 'string' ? record.issued_on : typeof record.issue_date === 'string' ? record.issue_date : undefined,
        due_on: typeof record.due_on === 'string' ? record.due_on : typeof record.due_date === 'string' ? record.due_date : undefined,
        status: normalizeInvoiceStatus(record.status ?? record.invoice_status),
        total_amount: toNumber(record.total_amount ?? record.amount_due ?? record.total),
        amount_paid: toNumber(record.amount_paid ?? record.paid_amount),
        outstanding_balance: toNumber(record.outstanding_balance)
    };
}
async function getInvoices(status) {
    const params = new URLSearchParams();
    if (status) params.set('status', status);
    const query = params.toString();
    const endpoint = `${__TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].API_BASE}/invoices${query ? `?${query}` : ''}`;
    const res = await fetch(endpoint);
    if (!res.ok) await parseError(res);
    const payload = await res.json();
    return {
        data: Array.isArray(payload.data) ? payload.data.map(normalizeInvoice) : [],
        summary: {
            total_invoices: toNumber(payload.summary?.total_invoices),
            pending: toNumber(payload.summary?.pending),
            paid: toNumber(payload.summary?.paid),
            cancelled: toNumber(payload.summary?.cancelled),
            outstanding_balance: toNumber(payload.summary?.outstanding_balance)
        }
    };
}
async function getInvoiceLineItems(invoiceId) {
    const res = await fetch(`${__TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].API_BASE}/invoices/${invoiceId}/line-items`);
    if (!res.ok) await parseError(res);
    const payload = await res.json();
    return Array.isArray(payload.data) ? payload.data : [];
}
async function getOutstandingBalances() {
    const res = await fetch(`${__TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].API_BASE}/invoices/outstanding-balance`);
    if (!res.ok) await parseError(res);
    const payload = await res.json();
    return {
        data: Array.isArray(payload.data) ? payload.data.map(normalizeInvoice) : [],
        total_outstanding_balance: toNumber(payload.total_outstanding_balance)
    };
}
async function recordPayment(payload) {
    const res = await fetch(`${__TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$config$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["default"].API_BASE}/payments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    if (!res.ok) await parseError(res);
}
}),
"[project]/frontend/src/pages/PaymentPage.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>PaymentPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/src/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/src/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$services$2f$paymentService$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/frontend/src/services/paymentService.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
const defaultSummary = {
    total_invoices: 0,
    pending: 0,
    paid: 0,
    cancelled: 0,
    outstanding_balance: 0
};
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-CA', {
        style: 'currency',
        currency: 'CAD'
    }).format(amount);
}
function formatDate(value) {
    if (!value) return '-';
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString();
}
function lineItemTotal(item) {
    if (typeof item.line_total === 'number') return item.line_total;
    if (typeof item.amount === 'number') return item.amount;
    return (item.quantity ?? 1) * (item.unit_price ?? 0);
}
function PaymentPage() {
    const [statusFilter, setStatusFilter] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])('All');
    const [invoices, setInvoices] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [summary, setSummary] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(defaultSummary);
    const [outstandingTotal, setOutstandingTotal] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(0);
    const [selectedInvoiceId, setSelectedInvoiceId] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [selectedLineItems, setSelectedLineItems] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [submitting, setSubmitting] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(false);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(null);
    const [paymentForm, setPaymentForm] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])({
        invoice_id: '',
        amount: '',
        payment_method: 'Card',
        paid_on: new Date().toISOString().slice(0, 10),
        notes: ''
    });
    const selectedInvoice = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useMemo"])(()=>invoices.find((invoice)=>invoice.invoice_id === selectedInvoiceId) ?? null, [
        invoices,
        selectedInvoiceId
    ]);
    const loadInvoices = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async (filter)=>{
        const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$services$2f$paymentService$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getInvoices"])(filter === 'All' ? undefined : filter);
        setInvoices(response.data);
        setSummary(response.summary);
        if (!response.data.length) {
            setSelectedInvoiceId(null);
            setSelectedLineItems([]);
            return;
        }
        const invoiceExists = response.data.some((invoice)=>invoice.invoice_id === selectedInvoiceId);
        const nextSelectedId = invoiceExists && selectedInvoiceId ? selectedInvoiceId : response.data[0].invoice_id;
        setSelectedInvoiceId(nextSelectedId);
        const lines = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$services$2f$paymentService$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getInvoiceLineItems"])(nextSelectedId);
        setSelectedLineItems(lines);
    }, [
        selectedInvoiceId
    ]);
    const loadOutstandingBalance = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async ()=>{
        const response = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$services$2f$paymentService$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getOutstandingBalances"])();
        setOutstandingTotal(response.total_outstanding_balance);
    }, []);
    const refreshData = (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useCallback"])(async (filter)=>{
        setLoading(true);
        setError(null);
        try {
            await Promise.all([
                loadInvoices(filter),
                loadOutstandingBalance()
            ]);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load payment data';
            setError(message);
        } finally{
            setLoading(false);
        }
    }, [
        loadInvoices,
        loadOutstandingBalance
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        void refreshData(statusFilter);
    }, [
        refreshData,
        statusFilter
    ]);
    async function handleSelectInvoice(invoiceId) {
        setSelectedInvoiceId(invoiceId);
        setPaymentForm((prev)=>({
                ...prev,
                invoice_id: String(invoiceId)
            }));
        try {
            const lines = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$services$2f$paymentService$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["getInvoiceLineItems"])(invoiceId);
            setSelectedLineItems(lines);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to load line items';
            setError(message);
            setSelectedLineItems([]);
        }
    }
    async function handleSubmitPayment(event) {
        event.preventDefault();
        const invoiceId = Number(paymentForm.invoice_id);
        const amount = Number(paymentForm.amount);
        if (!invoiceId || !Number.isFinite(invoiceId)) {
            setError('Please select an invoice');
            return;
        }
        if (!amount || amount <= 0) {
            setError('Payment amount must be greater than 0');
            return;
        }
        setSubmitting(true);
        setError(null);
        try {
            await (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$services$2f$paymentService$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["recordPayment"])({
                invoice_id: invoiceId,
                amount,
                payment_method: paymentForm.payment_method,
                paid_on: paymentForm.paid_on,
                notes: paymentForm.notes || undefined
            });
            setPaymentForm((prev)=>({
                    ...prev,
                    amount: '',
                    notes: ''
                }));
            await refreshData(statusFilter);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to record payment';
            setError(message);
        } finally{
            setSubmitting(false);
        }
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("main", {
        className: "page-payments",
        style: {
            padding: 20
        },
        children: [
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h1", {
                children: "Payments"
            }, void 0, false, {
                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                lineNumber: 160,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                style: {
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, minmax(0, 1fr))',
                    gap: 12,
                    marginBottom: 16
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("article", {
                        style: {
                            border: '1px solid #ddd',
                            borderRadius: 8,
                            padding: 12
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                children: "Total Invoices"
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 164,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                children: summary.total_invoices
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 165,
                                columnNumber: 21
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 163,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("article", {
                        style: {
                            border: '1px solid #ddd',
                            borderRadius: 8,
                            padding: 12
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                children: "Pending"
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 168,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                children: summary.pending
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 169,
                                columnNumber: 21
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 167,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("article", {
                        style: {
                            border: '1px solid #ddd',
                            borderRadius: 8,
                            padding: 12
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                children: "Paid"
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 172,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                children: summary.paid
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 173,
                                columnNumber: 21
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 171,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("article", {
                        style: {
                            border: '1px solid #ddd',
                            borderRadius: 8,
                            padding: 12
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                children: "Outstanding Balance"
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 176,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                children: formatCurrency(outstandingTotal || summary.outstanding_balance)
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 177,
                                columnNumber: 21
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 175,
                        columnNumber: 17
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                lineNumber: 162,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                style: {
                    display: 'flex',
                    gap: 8,
                    marginBottom: 12,
                    flexWrap: 'wrap'
                },
                children: [
                    'All',
                    'Pending',
                    'Paid',
                    'Cancelled'
                ].map((status)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                        onClick: ()=>setStatusFilter(status),
                        disabled: statusFilter === status || loading,
                        children: status
                    }, status, false, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 183,
                        columnNumber: 21
                    }, this))
            }, void 0, false, {
                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                lineNumber: 181,
                columnNumber: 13
            }, this),
            error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                style: {
                    color: '#c0392b',
                    marginBottom: 12
                },
                role: "alert",
                children: error
            }, void 0, false, {
                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                lineNumber: 194,
                columnNumber: 17
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                style: {
                    display: 'grid',
                    gridTemplateColumns: '2fr 1fr',
                    gap: 16,
                    alignItems: 'start'
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        style: {
                            border: '1px solid #ddd',
                            borderRadius: 8,
                            overflow: 'hidden'
                        },
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("table", {
                            style: {
                                width: '100%',
                                borderCollapse: 'collapse'
                            },
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("thead", {
                                    children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                        style: {
                                            background: '#f7f7f7'
                                        },
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                style: {
                                                    textAlign: 'left',
                                                    padding: 10
                                                },
                                                children: "Invoice"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 204,
                                                columnNumber: 33
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                style: {
                                                    textAlign: 'left',
                                                    padding: 10
                                                },
                                                children: "Student"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 205,
                                                columnNumber: 33
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                style: {
                                                    textAlign: 'left',
                                                    padding: 10
                                                },
                                                children: "Status"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 206,
                                                columnNumber: 33
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("th", {
                                                style: {
                                                    textAlign: 'right',
                                                    padding: 10
                                                },
                                                children: "Outstanding"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 207,
                                                columnNumber: 33
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 203,
                                        columnNumber: 29
                                    }, this)
                                }, void 0, false, {
                                    fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                    lineNumber: 202,
                                    columnNumber: 25
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tbody", {
                                    children: [
                                        invoices.map((invoice)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                                onClick: ()=>void handleSelectInvoice(invoice.invoice_id),
                                                style: {
                                                    cursor: 'pointer',
                                                    background: selectedInvoiceId === invoice.invoice_id ? '#eef6ff' : 'transparent',
                                                    borderTop: '1px solid #eee'
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        style: {
                                                            padding: 10
                                                        },
                                                        children: [
                                                            "#",
                                                            invoice.invoice_id
                                                        ]
                                                    }, void 0, true, {
                                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                        lineNumber: 221,
                                                        columnNumber: 37
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        style: {
                                                            padding: 10
                                                        },
                                                        children: invoice.student_name || '-'
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                        lineNumber: 222,
                                                        columnNumber: 37
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        style: {
                                                            padding: 10
                                                        },
                                                        children: invoice.status
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                        lineNumber: 223,
                                                        columnNumber: 37
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                        style: {
                                                            textAlign: 'right',
                                                            padding: 10
                                                        },
                                                        children: formatCurrency(invoice.outstanding_balance)
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                        lineNumber: 224,
                                                        columnNumber: 37
                                                    }, this)
                                                ]
                                            }, invoice.invoice_id, true, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 212,
                                                columnNumber: 33
                                            }, this)),
                                        !loading && !invoices.length && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("tr", {
                                            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("td", {
                                                colSpan: 4,
                                                style: {
                                                    padding: 16,
                                                    textAlign: 'center'
                                                },
                                                children: "No invoices found for this filter."
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 230,
                                                columnNumber: 37
                                            }, this)
                                        }, void 0, false, {
                                            fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                            lineNumber: 229,
                                            columnNumber: 33
                                        }, this)
                                    ]
                                }, void 0, true, {
                                    fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                    lineNumber: 210,
                                    columnNumber: 25
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                            lineNumber: 201,
                            columnNumber: 21
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 200,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("aside", {
                        style: {
                            border: '1px solid #ddd',
                            borderRadius: 8,
                            padding: 12
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                                style: {
                                    marginTop: 0
                                },
                                children: "Invoice Details"
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 240,
                                columnNumber: 21
                            }, this),
                            !selectedInvoice && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                children: "Select an invoice to see line items."
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 242,
                                columnNumber: 42
                            }, this),
                            selectedInvoice && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Fragment"], {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                                children: "Invoice:"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 247,
                                                columnNumber: 33
                                            }, this),
                                            " #",
                                            selectedInvoice.invoice_id
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 246,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                                children: "Issued:"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 250,
                                                columnNumber: 33
                                            }, this),
                                            " ",
                                            formatDate(selectedInvoice.issued_on)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 249,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                                children: "Due:"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 253,
                                                columnNumber: 33
                                            }, this),
                                            " ",
                                            formatDate(selectedInvoice.due_on)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 252,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                                children: "Total:"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 256,
                                                columnNumber: 33
                                            }, this),
                                            " ",
                                            formatCurrency(selectedInvoice.total_amount)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 255,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                                children: "Paid:"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 259,
                                                columnNumber: 33
                                            }, this),
                                            " ",
                                            formatCurrency(selectedInvoice.amount_paid)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 258,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("strong", {
                                                children: "Outstanding:"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 262,
                                                columnNumber: 33
                                            }, this),
                                            " ",
                                            formatCurrency(selectedInvoice.outstanding_balance)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 261,
                                        columnNumber: 29
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                                        children: "Line Items"
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 265,
                                        columnNumber: 29
                                    }, this),
                                    !selectedLineItems.length && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        children: "No line items available."
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 266,
                                        columnNumber: 59
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("ul", {
                                        style: {
                                            paddingLeft: 16
                                        },
                                        children: selectedLineItems.map((item, index)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("li", {
                                                style: {
                                                    marginBottom: 8
                                                },
                                                children: [
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        children: item.description || `Item ${index + 1}`
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                        lineNumber: 270,
                                                        columnNumber: 41
                                                    }, this),
                                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                        style: {
                                                            float: 'right'
                                                        },
                                                        children: formatCurrency(lineItemTotal(item))
                                                    }, void 0, false, {
                                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                        lineNumber: 271,
                                                        columnNumber: 41
                                                    }, this)
                                                ]
                                            }, `${selectedInvoice.invoice_id}-${index}`, true, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 269,
                                                columnNumber: 37
                                            }, this))
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 267,
                                        columnNumber: 29
                                    }, this)
                                ]
                            }, void 0, true)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 239,
                        columnNumber: 17
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                lineNumber: 199,
                columnNumber: 13
            }, this),
            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("section", {
                style: {
                    marginTop: 20,
                    border: '1px solid #ddd',
                    borderRadius: 8,
                    padding: 16
                },
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        style: {
                            marginTop: 0
                        },
                        children: "Record Payment"
                    }, void 0, false, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 281,
                        columnNumber: 17
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        onSubmit: handleSubmitPayment,
                        style: {
                            display: 'grid',
                            gap: 10,
                            maxWidth: 480
                        },
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                children: [
                                    "Invoice",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                        value: paymentForm.invoice_id,
                                        onChange: (event)=>setPaymentForm((prev)=>({
                                                    ...prev,
                                                    invoice_id: event.target.value
                                                })),
                                        required: true,
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "",
                                                children: "Select invoice"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 291,
                                                columnNumber: 29
                                            }, this),
                                            invoices.filter((invoice)=>invoice.status === 'Pending' && invoice.outstanding_balance > 0).map((invoice)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                    value: String(invoice.invoice_id),
                                                    children: [
                                                        "#",
                                                        invoice.invoice_id,
                                                        " - ",
                                                        invoice.student_name,
                                                        " (",
                                                        formatCurrency(invoice.outstanding_balance),
                                                        ")"
                                                    ]
                                                }, invoice.invoice_id, true, {
                                                    fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                    lineNumber: 295,
                                                    columnNumber: 37
                                                }, this))
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 286,
                                        columnNumber: 25
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 284,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                children: [
                                    "Amount",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        type: "number",
                                        min: "0.01",
                                        step: "0.01",
                                        value: paymentForm.amount,
                                        onChange: (event)=>setPaymentForm((prev)=>({
                                                    ...prev,
                                                    amount: event.target.value
                                                })),
                                        required: true
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 304,
                                        columnNumber: 25
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 302,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                children: [
                                    "Payment Method",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("select", {
                                        value: paymentForm.payment_method,
                                        onChange: (event)=>setPaymentForm((prev)=>({
                                                    ...prev,
                                                    payment_method: event.target.value
                                                })),
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "Card",
                                                children: "Card"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 320,
                                                columnNumber: 29
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "Cash",
                                                children: "Cash"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 321,
                                                columnNumber: 29
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "E-Transfer",
                                                children: "E-Transfer"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 322,
                                                columnNumber: 29
                                            }, this),
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("option", {
                                                value: "Bank Transfer",
                                                children: "Bank Transfer"
                                            }, void 0, false, {
                                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                                lineNumber: 323,
                                                columnNumber: 29
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 316,
                                        columnNumber: 25
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 314,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                children: [
                                    "Payment Date",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                        type: "date",
                                        value: paymentForm.paid_on,
                                        onChange: (event)=>setPaymentForm((prev)=>({
                                                    ...prev,
                                                    paid_on: event.target.value
                                                }))
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 329,
                                        columnNumber: 25
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 327,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("label", {
                                children: [
                                    "Notes",
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("textarea", {
                                        rows: 3,
                                        value: paymentForm.notes,
                                        onChange: (event)=>setPaymentForm((prev)=>({
                                                    ...prev,
                                                    notes: event.target.value
                                                })),
                                        placeholder: "Optional payment notes"
                                    }, void 0, false, {
                                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                        lineNumber: 338,
                                        columnNumber: 25
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 336,
                                columnNumber: 21
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$frontend$2f$src$2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                type: "submit",
                                disabled: submitting || loading,
                                children: submitting ? 'Saving Payment...' : 'Record Payment'
                            }, void 0, false, {
                                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                                lineNumber: 346,
                                columnNumber: 21
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                        lineNumber: 283,
                        columnNumber: 17
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
                lineNumber: 280,
                columnNumber: 13
            }, this)
        ]
    }, void 0, true, {
        fileName: "[project]/frontend/src/pages/PaymentPage.tsx",
        lineNumber: 159,
        columnNumber: 9
    }, this);
}
}),
];

//# sourceMappingURL=frontend_src_0f649856._.js.map