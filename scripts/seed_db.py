# scripts/seed_db.py

from app import create_app
from models import db, User, Customer, Invoice
from datetime import datetime

def seed_data():
    """Function to seed the database with initial data."""

    # Create some users
    admin = User(username="admin", email="admin@example.com")
    admin.set_password("password123")
    user1 = User(username="john_doe", email="john@example.com")
    user1.set_password("password123")
    user2 = User(username="jane_smith", email="jane@example.com")
    user2.set_password("password123")

    # Add users to the session
    db.session.add(admin)
    db.session.add(user1)
    db.session.add(user2)

    # Create some customers
    customer1 = Customer(name="John Doe", email="john.doe@example.com", phone="123-456-7890", address="123 Elm Street")
    customer2 = Customer(name="Jane Smith", email="jane.smith@example.com", phone="987-654-3210", address="456 Oak Avenue")

    # Add customers to the session
    db.session.add(customer1)
    db.session.add(customer2)

    # Create some invoices
    invoice1 = Invoice(
        invoice_number="INV-2024-001",
        amount=200.00,
        status="Pending",
        issue_date=datetime(2024, 1, 1),
        due_date=datetime(2024, 1, 31),
        description="Consulting services",
        customer=customer1,  # Link the invoice to customer1
        user=admin  # Link the invoice to admin
    )
    
    invoice2 = Invoice(
        invoice_number="INV-2024-002",
        amount=450.00,
        status="Paid",
        issue_date=datetime(2024, 1, 1),
        due_date=datetime(2024, 1, 31),
        description="Development services",
        customer=customer2,  # Link the invoice to customer2
        user=user1  # Link the invoice to user1
    )

    # Add invoices to the session
    db.session.add(invoice1)
    db.session.add(invoice2)

    # Commit the session to save data to the database
    db.session.commit()

if __name__ == "__main__":
    # Create the Flask app and context
    app = create_app()
    with app.app_context():
        # Call the seed_data function to populate the database
        seed_data()
        print("Database seeded with initial data.")
