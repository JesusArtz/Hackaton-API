from flask import jsonify, request
from src.models import User
from __init__ import token_required

@token_required
def get_user_info(): 
    user = User()
    return jsonify(user.get_user(token=request.headers['token']))

@token_required
def get_account_information():
    user = User(data=request.get_json())
    return jsonify(user.get_account_information())