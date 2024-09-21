# billing.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Invoice, Customer, User  # Import models
from services.payment_service import PaymentService  # Payment processing service (e.g., Stripe, PayPal)
from flask_login import login_required, current_user
from datetime import datetime


# Initialize the billing blueprint
billing = Blueprint('billing', __name__)

# Service responsible for processing payments
payment_service = PaymentService()

# Billing model choices
BILLING_MODELS = {
    'one-time': 'One-Time Payment',
    'subscription': 'Recurring Subscription',
    'usage-based': 'Usage-Based Billing',
    'custom': 'Custom Billing'
}

# Route: Create a new invoice for the customer
@billing.route('/invoices/create', methods=['GET', 'POST'])
@login_required
def create_invoice():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        amount = float(request.form['amount'])
        billing_method = request.form['billing_method']  # One-time, subscription, etc.
        
        # Create a new invoice for the customer
        invoice = Invoice(
            customer_id=customer_id,
            user_id=current_user.id,  # Logged-in user (merchant)
            amount=amount,
            billing_method=billing_method,
            status='unpaid',
            created_at=datetime.utcnow()
        )
        
        # Save the invoice
        db.session.add(invoice)
        db.session.commit()
        
        flash('Invoice created successfully!', 'success')
        return redirect(url_for('billing.manage_invoices'))
    
    # Render form to create invoice
    customers = Customer.query.filter_by(user_id=current_user.id).all()  # Get customers for the logged-in user
    return render_template('create_invoice.html', customers=customers, billing_models=BILLING_MODELS)


# Route: Manage all invoices for the current user
@billing.route('/invoices/manage')
@login_required
def manage_invoices():
    # Fetch all invoices for the logged-in user
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    return render_template('manage_invoices.html', invoices=invoices)


# Route: Pay an invoice
@billing.route('/invoices/pay/<int:invoice_id>', methods=['POST'])
@login_required
def pay_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    
    # Check if the invoice is unpaid
    if invoice.status == 'unpaid':
        # Call payment service to process payment
        success = payment_service.process_payment(invoice)
        
        if success:
            # Update invoice status
            invoice.status = 'paid'
            db.session.commit()
            flash('Invoice paid successfully!', 'success')
        else:
            flash('Payment failed. Please try again.', 'danger')
    
    return redirect(url_for('billing.manage_invoices'))


# Route: Manage subscriptions for recurring billing
@billing.route('/subscriptions/manage')
@login_required
def manage_subscriptions():
    # Fetch all recurring subscriptions for the logged-in user
    subscriptions = Invoice.query.filter_by(user_id=current_user.id, billing_method='subscription').all()
    return render_template('manage_subscriptions.html', subscriptions=subscriptions)


# Route: Handle different billing models for an invoice (e.g., one-time, recurring)
@billing.route('/invoices/billing_method/<int:invoice_id>', methods=['POST'])
@login_required
def update_billing_method(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    new_billing_method = request.form['billing_method']
    
    # Update billing method for the invoice
    if new_billing_method in BILLING_MODELS:
        invoice.billing_method = new_billing_method
        db.session.commit()
        flash('Billing method updated successfully!', 'success')
    else:
        flash('Invalid billing method.', 'danger')
    
    return redirect(url_for('billing.manage_invoices'))

