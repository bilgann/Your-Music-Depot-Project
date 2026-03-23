from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


def get_all_invoices():
    return _db().table("invoice").select("*").execute().data


def get_invoice_by_id(invoice_id):
    return _db().table("invoice").select("*").eq("invoice_id", invoice_id).execute().data


def create_invoice(data):
    return _db().table("invoice").insert(data).execute().data


def update_invoice(invoice_id, data):
    return _db().table("invoice").update(data).eq("invoice_id", invoice_id).execute().data


def delete_invoice(invoice_id):
    return _db().table("invoice").delete().eq("invoice_id", invoice_id).execute().data