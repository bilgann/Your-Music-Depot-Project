import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask, jsonify, request
from typing import Any, Dict, List, Optional, Tuple
from database import supabase

app = Flask(__name__)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _pick_first(record: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return default


def _normalize_status(raw_status: Any) -> str:
    text = str(raw_status or '').strip().lower()
    if text == 'paid':
        return 'Paid'
    if text == 'cancelled' or text == 'canceled':
        return 'Cancelled'
    return 'Pending'


def _find_existing_table(candidates: List[str]) -> str:
    for table in candidates:
        try:
            supabase.table(table).select('*').limit(1).execute()
            return table
        except Exception:
            continue
    return candidates[0]


INVOICE_TABLE = _find_existing_table(['invoice', 'invoices'])
PAYMENT_TABLE = _find_existing_table(['payment', 'payments'])


def _query_invoice_by_id(invoice_id: int) -> Optional[Dict[str, Any]]:
    id_columns = ['invoice_id', 'id']
    for column in id_columns:
        try:
            response = supabase.table(INVOICE_TABLE).select('*').eq(column, invoice_id).limit(1).execute()
            rows = response.data or []
            if rows:
                return rows[0]
        except Exception:
            continue
    return None


def _fetch_line_items(invoice_id: int) -> List[Dict[str, Any]]:
    line_item_tables = ['invoice_line_item', 'invoice_line_items', 'invoice_item', 'line_item', 'line_items']
    invoice_columns = ['invoice_id', 'invoiceId', 'id_invoice']

    for table in line_item_tables:
        for column in invoice_columns:
            try:
                response = supabase.table(table).select('*').eq(column, invoice_id).execute()
                rows = response.data or []
                if rows:
                    return rows
            except Exception:
                continue
    return []


def _serialize_invoice(invoice: Dict[str, Any], include_line_items: bool = False) -> Dict[str, Any]:
    invoice_id = int(_pick_first(invoice, ['invoice_id', 'id'], 0) or 0)
    status = _normalize_status(_pick_first(invoice, ['status', 'invoice_status']))
    line_items: List[Dict[str, Any]] = []

    if include_line_items:
        embedded = _pick_first(invoice, ['line_items', 'invoice_line_items'], [])
        if isinstance(embedded, list) and embedded:
            line_items = embedded
        else:
            line_items = _fetch_line_items(invoice_id)

    total_from_invoice = _to_float(_pick_first(invoice, ['total_amount', 'amount_due', 'total', 'invoice_total']))
    amount_paid = _to_float(_pick_first(invoice, ['amount_paid', 'paid_amount', 'payment_total']))

    if total_from_invoice <= 0 and line_items:
        total_from_invoice = sum(
            _to_float(_pick_first(item, ['line_total', 'amount', 'total']))
            or (_to_float(_pick_first(item, ['quantity'], 1.0)) * _to_float(_pick_first(item, ['unit_price', 'price'], 0.0)))
            for item in line_items
        )

    outstanding_balance = max(total_from_invoice - amount_paid, 0.0)

    if status != 'Cancelled':
        if outstanding_balance <= 0:
            status = 'Paid'
        else:
            status = 'Pending'

    payload = {
        **invoice,
        'invoice_id': invoice_id,
        'student_id': _pick_first(invoice, ['student_id', 'customer_id']),
        'student_name': _pick_first(invoice, ['student_name', 'customer_name', 'full_name'], 'Unknown Student'),
        'issued_on': _pick_first(invoice, ['issued_on', 'issue_date', 'created_at']),
        'due_on': _pick_first(invoice, ['due_on', 'due_date']),
        'status': status,
        'total_amount': round(total_from_invoice, 2),
        'amount_paid': round(amount_paid, 2),
        'outstanding_balance': round(outstanding_balance, 2),
    }

    if include_line_items:
        payload['line_items'] = line_items

    return payload


def _update_invoice_payment_totals(invoice_id: int, payment_amount: float) -> Optional[Dict[str, Any]]:
    invoice = _query_invoice_by_id(invoice_id)
    if not invoice:
        return None

    current_paid = _to_float(_pick_first(invoice, ['amount_paid', 'paid_amount', 'payment_total']))
    new_paid = current_paid + payment_amount
    serialized = _serialize_invoice({**invoice, 'amount_paid': new_paid}, include_line_items=False)

    update_payload = {
        'amount_paid': round(new_paid, 2),
        'status': serialized['status'],
    }

    for id_column in ['invoice_id', 'id']:
        try:
            supabase.table(INVOICE_TABLE).update(update_payload).eq(id_column, invoice_id).execute()
            return _query_invoice_by_id(invoice_id)
        except Exception:
            continue

    return invoice

@app.route('/students')
def students():
    response = supabase.table("student").select("*").execute()
    return jsonify(response.data)

@app.route('/instructors')
def instructors():
    response = supabase.table("instructor").select("*").execute()
    return jsonify(response.data)

@app.route('/invoices')
def invoices():
    response = supabase.table("invoice").select("*").execute()
    return jsonify(response.data)

@app.route('/lessons')
def lessons():
    response = supabase.table("lesson").select("*").execute()
    return jsonify(response.data)

@app.route('/rooms')
def rooms():
    response = supabase.table("room").select("*").execute()
    return jsonify(response.data)


@app.route('/api/students')
def api_students():
    return students()


@app.route('/api/instructors')
def api_instructors():
    return instructors()


@app.route('/api/rooms')
def api_rooms():
    return rooms()


@app.route('/api/invoices', methods=['GET'])
def api_invoices():
    status_filter = _normalize_status(request.args.get('status', '')) if request.args.get('status') else None
    include_line_items = request.args.get('includeLineItems', 'false').lower() == 'true'

    response = supabase.table(INVOICE_TABLE).select('*').execute()
    invoices = response.data or []

    serialized = [_serialize_invoice(invoice, include_line_items=include_line_items) for invoice in invoices]
    if status_filter:
        serialized = [invoice for invoice in serialized if invoice['status'] == status_filter]

    totals = {
        'total_invoices': len(serialized),
        'pending': sum(1 for invoice in serialized if invoice['status'] == 'Pending'),
        'paid': sum(1 for invoice in serialized if invoice['status'] == 'Paid'),
        'cancelled': sum(1 for invoice in serialized if invoice['status'] == 'Cancelled'),
        'outstanding_balance': round(sum(invoice['outstanding_balance'] for invoice in serialized), 2),
    }

    return jsonify({'data': serialized, 'summary': totals})


@app.route('/api/invoices/<int:invoice_id>/line-items', methods=['GET'])
def api_invoice_line_items(invoice_id: int):
    invoice = _query_invoice_by_id(invoice_id)
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    line_items = _fetch_line_items(invoice_id)
    return jsonify({'invoice_id': invoice_id, 'data': line_items})


@app.route('/api/invoices/outstanding-balance', methods=['GET'])
def api_outstanding_balance():
    response = supabase.table(INVOICE_TABLE).select('*').execute()
    invoices = response.data or []
    serialized = [_serialize_invoice(invoice, include_line_items=False) for invoice in invoices]

    outstanding = [invoice for invoice in serialized if invoice['status'] == 'Pending']
    total_outstanding = round(sum(invoice['outstanding_balance'] for invoice in outstanding), 2)

    return jsonify({
        'data': outstanding,
        'total_outstanding_balance': total_outstanding,
    })


@app.route('/api/payments', methods=['GET'])
def api_payments_get():
    response = supabase.table(PAYMENT_TABLE).select('*').order('created_at', desc=True).execute()
    return jsonify(response.data or [])


def _insert_payment(payload: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    payload_variants = [
        payload,
        {
            'invoice_id': payload['invoice_id'],
            'amount': payload['amount'],
            'payment_date': payload['paid_on'],
            'payment_method': payload['payment_method'],
            'notes': payload.get('notes'),
        },
        {
            'invoice_id': payload['invoice_id'],
            'amount_paid': payload['amount'],
            'paid_on': payload['paid_on'],
            'method': payload['payment_method'],
            'notes': payload.get('notes'),
        },
    ]

    last_error = None
    for item in payload_variants:
        try:
            response = supabase.table(PAYMENT_TABLE).insert(item).execute()
            rows = response.data or []
            if rows:
                return rows[0], None
        except Exception as exc:
            last_error = str(exc)

    return None, last_error or 'Failed to insert payment'


@app.route('/api/payments', methods=['POST'])
def api_payments_post():
    data = request.get_json(silent=True) or {}

    invoice_id = data.get('invoice_id')
    amount = _to_float(data.get('amount'))
    payment_method = (data.get('payment_method') or 'Card').strip()
    paid_on = data.get('paid_on') or data.get('payment_date')

    if not invoice_id:
        return jsonify({'error': 'invoice_id is required'}), 400
    if amount <= 0:
        return jsonify({'error': 'amount must be greater than 0'}), 400

    invoice = _query_invoice_by_id(int(invoice_id))
    if not invoice:
        return jsonify({'error': 'Invoice not found'}), 404

    normalized_invoice = _serialize_invoice(invoice, include_line_items=False)
    if normalized_invoice['status'] == 'Cancelled':
        return jsonify({'error': 'Cannot record payment for a cancelled invoice'}), 400
    if normalized_invoice['outstanding_balance'] <= 0:
        return jsonify({'error': 'Invoice is already fully paid'}), 400

    if amount > normalized_invoice['outstanding_balance']:
        return jsonify({'error': 'Payment amount exceeds outstanding balance'}), 400

    payment_payload = {
        'invoice_id': int(invoice_id),
        'amount': round(amount, 2),
        'payment_method': payment_method,
        'paid_on': paid_on,
        'notes': data.get('notes'),
    }

    created_payment, insert_error = _insert_payment(payment_payload)
    if insert_error:
        return jsonify({'error': insert_error}), 500

    updated_invoice = _update_invoice_payment_totals(int(invoice_id), amount)

    return jsonify({
        'payment': created_payment,
        'invoice': _serialize_invoice(updated_invoice or invoice, include_line_items=False),
    }), 201

if __name__ == '__main__':
    app.run(debug=True)