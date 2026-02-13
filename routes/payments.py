from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Payment, User
import requests
import os
import base64

payment_bp = Blueprint('payment', __name__)

PAYD_API_URL = "https://api.payd.io/v1"
PAYD_USERNAME = os.getenv('PAYD_USERNAME')
PAYD_PASSWORD = os.getenv('PAYD_PASSWORD')
PAYD_ACCOUNT = os.getenv('PAYD_ACCOUNT_USERNAME')

def get_payd_auth():
    credentials = f"{PAYD_USERNAME}:{PAYD_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()
    
    amount = data.get('amount', 9.99)
    currency = data.get('currency', 'USD')
    description = data.get('description', 'FlavorHub Premium Subscription')
    
    payment = Payment(
        user_id=user_id,
        amount=amount,
        currency=currency,
        status='pending'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # PayD API request
    payd_payload = {
        "amount": amount,
        "currency": currency,
        "description": description,
        "customer_email": user.email,
        "customer_name": user.username,
        "callback_url": f"{request.host_url}api/payments/callback",
        "return_url": f"{request.host_url}payment-success"
    }
    
    try:
        response = requests.post(
            f"{PAYD_API_URL}/payments",
            json=payd_payload,
            headers={
                "Authorization": get_payd_auth(),
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code in [200, 201]:
            payd_data = response.json()
            payment.payd_transaction_id = payd_data.get('transaction_id')
            payment.status = 'initiated'
            db.session.commit()
            
            return jsonify({
                'payment_id': payment.id,
                'payment_url': payd_data.get('payment_url'),
                'transaction_id': payment.payd_transaction_id
            }), 200
        else:
            payment.status = 'failed'
            db.session.commit()
            return jsonify({'error': 'Payment initiation failed', 'details': response.text}), 400
            
    except Exception as e:
        payment.status = 'failed'
        db.session.commit()
        return jsonify({'error': str(e)}), 500

@payment_bp.route('/callback', methods=['POST'])
def payment_callback():
    data = request.get_json()
    
    transaction_id = data.get('transaction_id')
    status = data.get('status')
    
    payment = Payment.query.filter_by(payd_transaction_id=transaction_id).first()
    
    if payment:
        payment.status = status
        db.session.commit()
        
        if status == 'completed':
            user = User.query.get(payment.user_id)
            # Grant premium access logic here
        
        return jsonify({'message': 'Callback processed'}), 200
    
    return jsonify({'error': 'Payment not found'}), 404

@payment_bp.route('/verify/<transaction_id>', methods=['GET'])
@jwt_required()
def verify_payment(transaction_id):
    user_id = int(get_jwt_identity())
    
    payment = Payment.query.filter_by(
        payd_transaction_id=transaction_id,
        user_id=user_id
    ).first()
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    return jsonify({
        'status': payment.status,
        'amount': payment.amount,
        'currency': payment.currency
    }), 200

@payment_bp.route('/history', methods=['GET'])
@jwt_required()
def payment_history():
    user_id = int(get_jwt_identity())
    payments = Payment.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': p.id,
        'amount': p.amount,
        'currency': p.currency,
        'status': p.status,
        'created_at': p.created_at.isoformat()
    } for p in payments]), 200
