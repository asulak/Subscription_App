# billing/payment_routes.py

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
