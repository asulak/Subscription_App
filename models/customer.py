# models/customer.py

from app import db
from datetime import datetime

class Customer(db.Model):
    """Represents a customer who receives invoices."""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for each customer
    name = db.Column(db.String(100), nullable=False)  # Customer's name
    email = db.Column(db.String(120), unique=True, nullable=False)  # Customer's email
    phone = db.Column(db.String(20), nullable=True)  # Customer's phone number
    address = db.Column(db.String(200), nullable=True)  # Customer's address
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Customer creation timestamp
    active = db.Column(db.Boolean, default=True)  # Status (active/inactive)

    # Establishes relationship to Invoice model, links it with customer relationship defined in Invoice
    invoices = db.relationship('Invoice', back_populates='customer', cascade='all, delete-orphan')

    def deactivate(self):
        """Deactivates the customer and related invoices."""
        self.active = False
        for invoice in self.invoices:
            invoice.status = 'Cancelled'
        db.session.commit()

    def __repr__(self):
        return f"<Customer {self.name} ({self.email})>"