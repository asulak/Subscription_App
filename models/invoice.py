# models/invoice.py

from datetime import datetime
from app import db

class Invoice(db.Model):
    """Represents an invoice for a customer."""
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the invoice
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)  # Invoice number, must be unique
    amount = db.Column(db.Float, nullable=False)  # Amount to be paid
    status = db.Column(db.String(20), default='Pending')  # Invoice status (e.g., 'Pending', 'Paid', 'Overdue')
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)  # Date when the invoice was issued
    due_date = db.Column(db.DateTime, nullable=False)  # Date when the invoice is due
    description = db.Column(db.Text, nullable=True)  # Optional description of the invoice

    # Foreign keys linking invoice to a customer and user (vendor)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Links each invoice to the Customer model
    customer = db.relationship('Customer', back_populates='invoices') 
    # Links each invoice to the User model 
    user = db.relationship('User', back_populates='invoices') 
    
    def mark_paid(self):
        """
        Marks the invoice as paid and logs the action
        """
        self.status = 'Paid'
        db.session.commit()
        
    def is_overdue(self):
        """
        Checks if the invoice is overdue.
        """
        return datetime.utcnow() > self.due_date and self.status == "Pending"
    
    def send_reminder(self):
        """Send a reminder for this invoice."""
        # Pseudocode for sending a reminder (implement actual email sending logic)
        print(f"Reminder sent to {self.customer.email} for Invoice {self.invoice_number}")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.amount} - {self.status}>"
