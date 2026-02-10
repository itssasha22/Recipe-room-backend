from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User
import cloudinary
import cloudinary.uploader
import os

auth_bp = Blueprint('auth', __name__)

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if 'username' in data:
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Username already taken'}), 400
            user.username = data['username']
        
        if 'email' in data:
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Email already taken'}), 400
            user.email = data['email']
        
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/upload-image', methods=['POST'])
@jwt_required()
def upload_profile_image():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image = request.files['image']
        if image.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        result = cloudinary.uploader.upload(image)
        user.profile_image = result['secure_url']
        db.session.commit()
        
        return jsonify({'image_url': result['secure_url']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500