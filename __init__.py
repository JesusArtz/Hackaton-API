from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import jwt
from uuid import uuid4

APP = Flask(__name__)
APP.config['SECRET_KEY'] = str(uuid4())
CORS(APP)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'token' in request.headers:
            token = request.headers['token']

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            jwt.decode(token, APP.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        
        return f(*args, **kwargs)

    return decorated