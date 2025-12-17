
import json
import os
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime

# --- FILE-BASED "DATABASE" SETUP ---
DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_users(users):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Initialize utilities
bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data or 'name' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        users = load_users()
        
        # Check if email exists
        if any(u['email'] == data['email'] for u in users):
            return jsonify({'error': 'User already exists'}), 400
        
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        new_user = {
            'id': str(len(users) + 1),  # Simple ID generation
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        users.append(new_user)
        save_users(users)
        
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        users = load_users()
        user = next((u for u in users if u['email'] == data['email']), None)
        
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            access_token = create_access_token(identity=user['id'], expires_delta=datetime.timedelta(days=1))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'email': user['email']
                }
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_user_profile():
    current_user_id = get_jwt_identity()
    users = load_users()
    user = next((u for u in users if u['id'] == current_user_id), None)
    
    if user:
        return jsonify({
             'id': user['id'],
             'name': user['name'],
             'email': user['email']
        }), 200
    
    return jsonify({'error': 'User not found'}), 404
