from flask import jsonify, request
from __init__ import token_required
from src.models import Operations   

@token_required
def save_transactions():
    data = request.get_json()
    operations = Operations(data)
    return jsonify(operations.save_transactions())