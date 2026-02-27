import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask, jsonify
from database import supabase

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)