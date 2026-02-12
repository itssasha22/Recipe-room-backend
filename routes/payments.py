from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models import Payment, User
import requests

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    payment = Payment(
        user_id=user_id,
        amount=data['amount'],
        currency=data.get('currency', 'USD')
    )
    
    # PayD API integration
    payd_response = requests.post('https://api.payd.com/payments', {
        'amount': data['amount'],
        'currency': payment.currency,
        'user_id': user_id
    })
    
    if payd_response.status_code == 200:
        payment.payd_transaction_id = payd_response.json()['transaction_id']
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'payment_id': payment.id,
            'payd_url': payd_response.json()['payment_url']
        }), 200
    
    return jsonify({'error': 'Payment initiation failed'}), 400

@payment_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    data = request.get_json()
    
    payment = Payment.query.filter_by(
        payd_transaction_id=data['transaction_id']
    ).first()
    
    if payment:
        payment.status = data['status']
        db.session.commit()
        
        return jsonify({'message': 'Webhook processed'}), 200
    
    return jsonify({'error': 'Payment not found'}), 404