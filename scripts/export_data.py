# scripts/export_data.py

import csv
from app import create_app
from models import db, User, Customer

def export_users_to_csv(file_path='exported_users.csv'):
    """
    Export user data to a CSV file.
    
    Args:
        file_path (str): Path to the CSV file where the user data will be saved.
    """
    users = User.query.all()

    # Define the header
    fieldnames = ['id', 'username', 'email', 'role', 'confirmed', 'active', 'created_at']

    # Open the file and write data
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for user in users:
            writer.writerow({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'confirmed': user.confirmed,
                'active': user.active,
                'created_at': user.created_at
            })

    print(f"User data has been exported to {file_path}.")


def export_customers_to_csv(file_path='exported_customers.csv'):
    """
    Export customer data to a CSV file.
    
    Args:
        file_path (str): Path to the CSV file where the customer data will be saved.
    """
    customers = Customer.query.all()

    # Define the header
    fieldnames = ['id', 'name', 'email', 'phone', 'address', 'created_at']

    # Open the file and write data
    with open(file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for customer in customers:
            writer.writerow({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'address': customer.address,
                'created_at': customer.created_at
            })

    print(f"Customer data has been exported to {file_path}.")


if __name__ == "__main__":
    # Create the Flask app and context
    app = create_app()
    with app.app_context():
        # Export user data
        export_users_to_csv()

        # Export customer data
        export_customers_to_csv()
