import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import supabase

def get_all_invoices():
    return supabase.table("invoice").select("*").execute().data

def get_invoice_by_id(invoice_id):
    return supabase.table("invoice").select("*").eq("invoice_id", invoice_id).execute().data

def create_invoice(data):
    return supabase.table("invoice").insert(data).execute().data

def update_invoice(invoice_id, data):
    return supabase.table("invoice").update(data).eq("invoice_id", invoice_id).execute().data

def delete_invoice(invoice_id):
    return supabase.table("invoice").delete().eq("invoice_id", invoice_id).execute().data