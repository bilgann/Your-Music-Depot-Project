# Payment Feature Guide

Date: 2026-03-22

This guide explains what was implemented for invoices and payments, how data flows, and how to test everything end to end.

## 1) What was built

### Backend
- Added API endpoints for invoices and payments in backend/app.py.
- Added invoice status normalization to exactly:
  - Pending
  - Paid
  - Cancelled
- Added invoice summary metrics:
  - Total invoices
  - Pending count
  - Paid count
  - Cancelled count
  - Outstanding balance total
- Added invoice line item retrieval endpoint.
- Added payment recording endpoint with validation.
- Added outstanding balance endpoint.
- Added compatibility logic for common table naming variations in Supabase:
  - invoice or invoices
  - payment or payments
  - multiple possible line-item table names

### Frontend
- Created payment service layer in frontend/src/services/paymentService.ts.
- Replaced placeholder payment page with working UI in frontend/src/pages/PaymentPage.tsx.
- Added route entry in frontend/src/app/payments/page.tsx.

## 2) API endpoints

### GET /api/invoices
Purpose: Fetch invoices and summary.

Optional query params:
- status: Pending, Paid, or Cancelled
- includeLineItems: true or false

Response shape:
- data: invoice array
- summary: totals object

### GET /api/invoices/:invoice_id/line-items
Purpose: Fetch line items for one invoice.

Response shape:
- invoice_id
- data: line item array

### GET /api/invoices/outstanding-balance
Purpose: Fetch all pending invoices plus total outstanding amount.

Response shape:
- data: pending invoices
- total_outstanding_balance

### GET /api/payments
Purpose: Fetch payment history.

### POST /api/payments
Purpose: Record a payment and update invoice totals/status.

Request body fields:
- invoice_id (required)
- amount (required, must be greater than 0)
- payment_method (optional, default Card)
- paid_on (optional)
- notes (optional)

Validation rules:
- Invoice must exist
- Cannot pay cancelled invoice
- Cannot overpay beyond outstanding balance
- Cannot pay invoice that is already fully paid

## 3) Frontend flow

1. Payment page loads
- Calls GET /api/invoices
- Calls GET /api/invoices/outstanding-balance

2. Invoice selection
- Click invoice row
- Calls GET /api/invoices/:invoice_id/line-items
- Shows details panel and line items

3. Record payment
- Submit form
- Calls POST /api/payments
- Reloads invoice list and outstanding totals

## 4) Files changed

- backend/app.py
- frontend/src/services/paymentService.ts
- frontend/src/pages/PaymentPage.tsx
- frontend/src/app/payments/page.tsx

## 5) Manual test checklist

## A. Start backend
1. Open terminal in backend folder.
2. Ensure .env contains SUPABASE_URL and SUPABASE_KEY.
3. Start Flask app.

Expected: backend responds on port 5000.

## B. Start frontend
1. Open terminal in frontend/src folder.
2. Run Next dev server.
3. Open the app and navigate to /payments.

Expected: payments page loads invoice table and summary cards.

## C. Verify invoice list and status
1. Confirm each invoice shows one of Pending, Paid, or Cancelled.
2. Switch filter tabs: All, Pending, Paid, Cancelled.

Expected: list updates for each filter.

## D. Verify line items
1. Click an invoice row.
2. Confirm details panel updates.
3. Confirm line items are shown for that invoice.

Expected: line items endpoint is called and rendered.

## E. Verify record payment
1. Choose a pending invoice in form.
2. Enter amount less than or equal to outstanding balance.
3. Submit.

Expected:
- Success without page crash
- Invoice amount_paid increases
- Outstanding balance decreases
- Status updates to Paid when outstanding reaches 0

## F. Verify error cases
Try each and confirm friendly error message:
- amount is 0
- amount larger than outstanding
- invoice_id missing
- paying cancelled invoice

## 6) Suggested API smoke tests (Postman or Thunder Client)

GET http://localhost:5000/api/invoices
GET http://localhost:5000/api/invoices?status=Pending
GET http://localhost:5000/api/invoices/outstanding-balance
GET http://localhost:5000/api/invoices/1/line-items
POST http://localhost:5000/api/payments
Body example:
{
  "invoice_id": 1,
  "amount": 25,
  "payment_method": "Card",
  "paid_on": "2026-03-22",
  "notes": "Partial payment"
}

## 7) Troubleshooting

- If payments page is blank:
  - Verify frontend is running.
  - Verify backend is running.
  - Verify API base URL points to backend.

- If backend returns authentication errors:
  - Check SUPABASE_URL and SUPABASE_KEY.

- If line items are always empty:
  - Confirm your DB line-item table name and invoice foreign key column.
  - Adjust table/column mapping in backend/app.py if your schema uses custom names.

## 8) Next improvements

- Add automated tests:
  - Backend: pytest + Flask test client
  - Frontend: Playwright or Cypress for end-to-end
- Add payment history table in UI
- Add date range filters for invoices
- Add CSV export for outstanding balances
