# customer_portal/routes.py

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.manage_customer import get_customer_by_id, get_invoices_for_customer

customer_portal = Blueprint('customer_portal', __name__)

@customer_portal.route('/my-invoices', methods=['GET'])
@login_required
def my_invoices():
    """View all invoices for the logged-in customer."""
    if not current_user.customer:
        return jsonify({'error': 'Customer not found'}), 404

    invoices = get_invoices_for_customer(current_user.customer.id)
    return jsonify([{
        'invoice_number': inv.invoice_number,
        'amount': inv.amount,
        'status': inv.status,
        'due_date': inv.due_date.isoformat()
    } for inv in invoices])

@customer_portal.route('/my-subscription', methods=['GET'])
@login_required
def my_subscription():
    """View the current subscription for the logged-in customer."""
    if not current_user.customer or not current_user.customer.billing_model:
        return jsonify({'error': 'No active subscription found'}), 404

    subscription = current_user.customer.billing_model
    return jsonify({
        'name': subscription.name,
        'price': subscription.price,
        'billing_cycle': subscription.billing_cycle,
        'features': subscription.features
    })
