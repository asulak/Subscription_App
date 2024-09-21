# scripts/generate_test_data.py

from faker import Faker
from app import create_app
from models import db, User, Customer, Invoice
from datetime import datetime, timedelta
import random

def generate_users(num_users=10):
    """
    Generate a specified number of test users and add them to the database.
    
    Args:
        num_users (int): Number of test users to generate.
    """
    fake = Faker()
    roles = ['user', 'admin']  # Different user roles

    for _ in range(num_users):
        username = fake.user_name()
        email = fake.email()
        role = random.choice(roles)

        user = User(username=username, email=email, role=role)
        user.set_password("testpassword123")  # Set a default test password

        db.session.add(user)
    
    db.session.commit()
    print(f"Generated {num_users} users.")

def generate_customers(num_customers=20):
    """
    Generate a specified number of test customers and add them to the database.
    
    Args:
        num_customers (int): Number of test customers to generate.
    """
    fake = Faker()

    for _ in range(num_customers):
        name = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        address = fake.address()

        customer = Customer(name=name, email=email, phone=phone, address=address)

        db.session.add(customer)
    
    db.session.commit()
    print(f"Generated {num_customers} customers.")

def generate_invoices(num_invoices=50):
    """
    Generate a specified number of test invoices and add them to the database.
    
    Args:
        num_invoices (int): Number of test invoices to generate.
    """
    fake = Faker()
    users = User.query.all()
    customers = Customer.query.all()
    statuses = ['Pending', 'Paid', 'Overdue']  # Different invoice statuses

    for _ in range(num_invoices):
        user = random.choice(users)  # Randomly assign a user
        customer = random.choice(customers)  # Randomly assign a customer
        amount = round(random.uniform(50, 1000), 2)  # Random invoice amount
        issue_date = fake.date_between(start_date='-1y', end_date='today')  # Issue date within the last year
        due_date = issue_date + timedelta(days=30)  # Due date 30 days after issue date
        status = random.choice(statuses)  # Random status

        invoice = Invoice(
            invoice_number=fake.unique.bothify(text='INV-####-####'),
            amount=amount,
            status=status,
            issue_date=issue_date,
            due_date=due_date,
            description=fake.sentence(),
            customer=customer,
            user=user
        )

        db.session.add(invoice)
    
    db.session.commit()
    print(f"Generated {num_invoices} invoices.")

if __name__ == "__main__":
    # Create the Flask app and context
    app = create_app()
    with app.app_context():
        # Generate test data
        generate_users(num_users=10)         # Generate 10 test users
        generate_customers(num_customers=20) # Generate 20 test customers
        generate_invoices(num_invoices=50)   # Generate 50 test invoices
