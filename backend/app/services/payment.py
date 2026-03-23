from backend.app.singletons.database import DatabaseConnection


def _db():
    return DatabaseConnection().client


def get_all_payments():
    return _db().table("payment").select("*").execute().data


def get_payment_by_id(payment_id):
    return _db().table("payment").select("*").eq("payment_id", payment_id).execute().data


def create_payment(data):
    return _db().table("payment").insert(data).execute().data


def update_payment(payment_id, data):
    return _db().table("payment").update(data).eq("payment_id", payment_id).execute().data


def delete_payment(payment_id):
    return _db().table("payment").delete().eq("payment_id", payment_id).execute().data