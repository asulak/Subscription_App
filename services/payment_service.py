# services/payment_service.py

class PaymentService:
    def process_payment(self, invoice):
        # Call payment gateway API (e.g., Stripe or PayPal)
        # Validate the payment, and return True if successful, False otherwise.
        try:
            # Code for interacting with payment gateway goes here
            # e.g., charge customer, validate response
            return True  # Return True on success
        except Exception as e:
            print(f"Payment failed: {e}")
            return False  # Return False on failure
