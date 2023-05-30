from flask import jsonify, request
from src.models import User

def register():
    data = request.get_json()
    user = User(data)
    return jsonify(user.register())