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

if __name__ == '__main__':
    app.run(debug=True)