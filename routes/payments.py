from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from requests.auth import HTTPBasicAuth
from models import db, Payment, User
import requests

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate required fields
    if not data.get('amount') or not data.get('phone_number'):
        return jsonify({'error': 'amount and phone_number are required'}), 400

    payment = Payment(
        user_id=user_id,
        amount=data['amount'],
        currency=data.get('currency', 'KES')
    )

    # PayD API integration — Basic Auth + M-Pesa collection
    payd_response = requests.post(
        f"{current_app.config['PAYD_API_URL']}/api/v2/payments",
        auth=HTTPBasicAuth(
            current_app.config['PAYD_USERNAME'],
            current_app.config['PAYD_PASSWORD']
        ),
        json={
            'username': current_app.config['PAYD_ACCOUNT_USERNAME'],
            'channel': 'MPESA',
            'amount': data['amount'],
            'phone_number': data['phone_number'],
            'narration': data.get('narration', 'Recipe Room payment'),
            'currency': payment.currency,
            'callback_url': data.get('callback_url', request.host_url.rstrip('/') + '/api/payments/webhook')
        }
    )

    if payd_response.status_code in (200, 201, 202):
        response_data = payd_response.json()
        payment.payd_transaction_id = response_data.get('transaction_reference')
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            'payment_id': payment.id,
            'transaction_reference': payment.payd_transaction_id,
            'payment_method': response_data.get('payment_method'),
            'status': response_data.get('status'),
            'message': 'STK push sent, check your phone'
        }), 200

    return jsonify({
        'error': 'Payment initiation failed',
        'details': payd_response.json() if payd_response.content else payd_response.text
    }), payd_response.status_code

@payment_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    data = request.get_json()
    
    # Verify webhook payload (if PayD provides a signature or token)
    payment = Payment.query.filter_by(
        payd_transaction_id=data['transaction_id']
    ).first()
    
    if payment:
        payment.status = data['status']
        db.session.commit()
        return jsonify({'message': 'Webhook processed'}), 200
    
    return jsonify({'error': 'Payment not found'}), 404