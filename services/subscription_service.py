# services/subscription_service.py

from models import db, SubscriptionPlan

def create_subscription_plan(name, price, billing_cycle, description=None, features=None):
    """Create a new subscription plan."""
    try:
        plan = SubscriptionPlan(
            name=name,
            description=description,
            price=price,
            billing_cycle=billing_cycle,
            features=features
        )
        db.session.add(plan)
        db.session.commit()
        return plan
    except Exception as e:
        db.session.rollback()
        raise Exception(f"Failed to create subscription plan: {str(e)}")

def get_all_subscription_plans():
    """Retrieve all subscription plans."""
    return SubscriptionPlan.query.all()
