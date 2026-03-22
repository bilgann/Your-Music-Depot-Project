import config from '../config'

export type InvoiceStatus = 'Pending' | 'Paid' | 'Cancelled'

export type Invoice = {
  invoice_id: number
  student_id?: number
  student_name?: string
  issued_on?: string
  due_on?: string
  status: InvoiceStatus
  total_amount: number
  amount_paid: number
  outstanding_balance: number
}

export type InvoiceLineItem = {
  id?: number
  description?: string
  quantity?: number
  unit_price?: number
  amount?: number
  line_total?: number
}

export type InvoiceSummary = {
  total_invoices: number
  pending: number
  paid: number
  cancelled: number
  outstanding_balance: number
}

export type OutstandingBalanceResponse = {
  data: Invoice[]
  total_outstanding_balance: number
}

export type RecordPaymentPayload = {
  invoice_id: number
  amount: number
  payment_method: string
  paid_on?: string
  notes?: string
}

function extractErrorMessage(raw: unknown): string {
  if (typeof raw === 'string' && raw.trim()) return raw

  if (raw && typeof raw === 'object') {
    const obj = raw as Record<string, unknown>
    if (typeof obj.error === 'string' && obj.error) return obj.error
    if (typeof obj.message === 'string' && obj.message) return obj.message
    if (typeof obj.details === 'string' && obj.details) return obj.details
  }

  return 'Request failed'
}

async function parseError(res: Response): Promise<never> {
  try {
    const data = await res.json()
    throw new Error(extractErrorMessage(data))
  } catch {
    const text = await res.text()
    throw new Error(extractErrorMessage(text) || `Request failed: ${res.status}`)
  }
}

function toNumber(value: unknown): number {
  const asNumber = Number(value)
  return Number.isFinite(asNumber) ? asNumber : 0
}

function normalizeInvoiceStatus(value: unknown): InvoiceStatus {
  const normalized = String(value ?? '').trim().toLowerCase()
  if (normalized === 'paid') return 'Paid'
  if (normalized === 'cancelled' || normalized === 'canceled') return 'Cancelled'
  return 'Pending'
}

function normalizeInvoice(raw: unknown): Invoice {
  const record = (raw ?? {}) as Record<string, unknown>

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
  }
}

export async function getInvoices(status?: InvoiceStatus): Promise<{ data: Invoice[]; summary: InvoiceSummary }> {
  const params = new URLSearchParams()
  if (status) params.set('status', status)

  const query = params.toString()
  const endpoint = `${config.API_BASE}/invoices${query ? `?${query}` : ''}`
  const res = await fetch(endpoint)
  if (!res.ok) await parseError(res)

  const payload = (await res.json()) as {
    data?: unknown[]
    summary?: Partial<InvoiceSummary>
  }

  return {
    data: Array.isArray(payload.data) ? payload.data.map(normalizeInvoice) : [],
    summary: {
      total_invoices: toNumber(payload.summary?.total_invoices),
      pending: toNumber(payload.summary?.pending),
      paid: toNumber(payload.summary?.paid),
      cancelled: toNumber(payload.summary?.cancelled),
      outstanding_balance: toNumber(payload.summary?.outstanding_balance)
    }
  }
}

export async function getInvoiceLineItems(invoiceId: number): Promise<InvoiceLineItem[]> {
  const res = await fetch(`${config.API_BASE}/invoices/${invoiceId}/line-items`)
  if (!res.ok) await parseError(res)

  const payload = (await res.json()) as { data?: unknown[] }
  return Array.isArray(payload.data) ? (payload.data as InvoiceLineItem[]) : []
}

export async function getOutstandingBalances(): Promise<OutstandingBalanceResponse> {
  const res = await fetch(`${config.API_BASE}/invoices/outstanding-balance`)
  if (!res.ok) await parseError(res)

  const payload = (await res.json()) as {
    data?: unknown[]
    total_outstanding_balance?: number
  }

  return {
    data: Array.isArray(payload.data) ? payload.data.map(normalizeInvoice) : [],
    total_outstanding_balance: toNumber(payload.total_outstanding_balance)
  }
}

export async function recordPayment(payload: RecordPaymentPayload): Promise<void> {
  const res = await fetch(`${config.API_BASE}/payments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!res.ok) await parseError(res)
}