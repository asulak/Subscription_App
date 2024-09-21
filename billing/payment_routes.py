# billing/payment_routes.py

from flask import Blueprint, request, jsonify, current_app
import stripe
from plaid import Client
from models import db, Customer, User  # Import your models
from services.stripe_service import create_stripe_bank_account  # Import the Stripe service function
from flask_login import current_user  # To manage session and user data

# Create a blueprint for payment-related routes
payment = Blueprint('payment', __name__)

@payment.route('/create-stripe-customer', methods=['POST'])
def create_stripe_customer():
    """Create a Stripe customer for a verified customer with a linked bank account."""
    data = request.get_json()
    customer_id = data.get('customer_id')

    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    if not customer.plaid_access_token:
        return jsonify({'error': 'Customer has not linked a bank account via Plaid'}), 400

    try:
        # Create a Stripe customer
        stripe_customer = stripe.Customer.create(
            email=customer.email,
            name=customer.name,
        )

        # Save Stripe customer ID to the customer in the database
        customer.stripe_customer_id = stripe_customer['id']
        db.session.commit()

        # Create the Stripe bank account
        bank_account = create_stripe_bank_account(
            stripe_customer_id=stripe_customer['id'],
            account_data={
                'name': customer.bank_account_name,
                'routing_number': 'your_routing_number',  # Replace with routing number retrieved from Plaid
                'account_number': 'your_account_number',  # Replace with account number retrieved from Plaid
            }
        )

        return jsonify({
            'message': 'Stripe customer created and bank account linked',
            'stripe_customer_id': stripe_customer['id'],
            'stripe_bank_account': bank_account
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@payment.route('/create-link-token', methods=['POST'])
def create_link_token():
    """Create a Plaid link token for the frontend."""
    try:
        client = current_app.plaid_client
        response = client.LinkToken.create({
            'user': {'client_user_id': current_user.id},  # Assuming the user is logged in and current_user is available
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

@payment.route('/exchange-public-token', methods=['POST'])
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

@payment.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Webhook signature verification failed'}), 400

    # Handle different event types
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Update your database with the payment status
        # e.g., mark invoice as paid

    # Handle other event types as needed

    return jsonify({'status': 'success'}), 200
