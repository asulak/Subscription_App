# models/role.py

from app import db

class Role(db.Model):
    """Represents a user role for access control."""
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'admin', 'vendor', 'customer'
    description = db.Column(db.String(250), nullable=True)

    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f"<Role {self.name}>"
