# billing/plaid_routes.py

from flask import Blueprint, request, jsonify, current_app
from plaid import Client
import stripe
from models import db, Customer

plaid_routes = Blueprint('plaid', __name__)

@plaid_routes.route('/create-link-token', methods=['POST'])
def create_link_token():
    """Create a Plaid link token for the frontend."""
    try:
        client = current_app.plaid_client
        response = client.LinkToken.create({
            'user': {'client_user_id': 'unique_user_id'},
            'client_name': 'Your App Name',
            'products': ['auth', 'transactions'],
            'country_codes': ['US'],
            'language': 'en',
            'webhook': 'https://your-app.com/webhook',
            'link_customization_name': 'default',
        })
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@plaid_routes.route('/exchange-public-token', methods=['POST'])
def exchange_public_token():
    """Exchange the public token from Plaid Link for an access token and retrieve bank account details."""
    data = request.get_json()
    public_token = data.get('public_token')
    customer_id = data.get('customer_id')

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    try:
        client = current_app.plaid_client
        # Exchange the public token for an access token and item ID
        exchange_response = client.Item.public_token.exchange(public_token)
        access_token = exchange_response['access_token']
        item_id = exchange_response['item_id']

        # Get bank account details
        accounts_response = client.Auth.get(access_token)
        account = accounts_response['accounts'][0]  # Assuming the first account is the one we want

        # Save account information to the customer in your database
        customer.plaid_access_token = access_token
        customer.plaid_item_id = item_id
        customer.bank_account_id = account['account_id']
        customer.bank_account_last4 = account['mask']
        customer.bank_account_name = account['name']
        db.session.commit()

        return jsonify({
            'message': 'Bank account information saved',
            'bank_account_last4': customer.bank_account_last4,
            'bank_account_name': customer.bank_account_name
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # services/plaid_service.py

def initiate_micro_deposit_verification(access_token, account_id):
    """Initiate micro-deposit verification for a bank account."""
    try:
        response = current_app.plaid_client.Auth.micro_deposits(
            access_token, 
            account_id=account_id
        )
        return response
    except Exception as e:
        raise Exception(f"Failed to initiate micro-deposit verification: {str(e)}")

def verify_micro_deposits(access_token, account_id, amounts):
    """Verify micro-deposits by confirming the deposited amounts."""
    try:
        response = current_app.plaid_client.Auth.verify_micro_deposits(
            access_token,
            account_id=account_id,
            amounts=amounts  # List of two amounts e.g., [0.12, 0.34]
        )
        return response
    except Exception as e:
        raise Exception(f"Failed to verify micro-deposits: {str(e)}")


