from datetime import datetime
from flask import current_app
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from sqlalchemy.exc import IntegrityError
import re
from models.role import Role  # Import the Role model

class User(db.Model, UserMixin):
    """Represents a user in the system with enhanced functionality."""
    
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    email = db.Column(db.String(120), unique=True, nullable=False)  # User email
    username = db.Column(db.String(50), unique=True, nullable=False)  # User's username
    password_hash = db.Column(db.String(128), nullable=False)  # Hashed password
    confirmed = db.Column(db.Boolean, default=False)  # Email confirmed status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # User creation timestamp
    last_login = db.Column(db.DateTime)  # Stores the last login timestamp
    role = db.Column(db.String(50), default='user')  # Role (admin, user, etc.)
    active = db.Column(db.Boolean, default=True)  # Account status (active/inactive)
    
    # Relationship to invoices
    invoices = db.relationship('Invoice', back_populates='user', cascade='all, delete-orphan')

    # Other methods (set_password, check_password, etc.) remain the same as provided earlier

    def __repr__(self):
        return f"<User {self.username} - {self.email}>"

    ### Password Management

    def set_password(self, password):
        """Hashes and stores the user's password securely with strong validation."""
        # Ensure user follows secure password practices
        if not self.validate_password(password):
            current_app.logger.error(f"Password does not meet complexity requirements for user {self.email}")
            raise ValueError("Password does not meet complexity requirements.")
        # Ensures password is stored securely using hashing algorithm
        self.password_hash = generate_password_hash(password)
        current_app.logger.info(f"Password set for user {self.email}")

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        # You can add a delay here if you want to protect against brute-force attacks
        if not check_password_hash(self.password_hash, password):
            current_app.logger.warning(f"Failed login attempt for user {self.email}")
            return False
        current_app.logger.info(f"Successful password check for user {self.email}")
        return True


    # Validation methods
    
    @staticmethod
    def validate_password(password):
        """
        Validates that the password meets the following complexity rules:
        - Minimum length: 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    ### Account Management

    def mark_login(self):
        """Updates the user's last login timestamp and logs the activity."""
        # Track the login activity, possibly storing IP address, browser information, etc.
        self.last_login = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"User {self.email} logged in at {self.last_login}")


    def deactivate_account(self, reason=None):
        """Deactivates the user's account with an optional reason."""
        self.active = False
        self.deactivation_reason = reason if reason else "No reason provided"
        self.deactivated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"User {self.email} deactivated their account. Reason: {self.deactivation_reason}")

    def activate_account(self):
        """Reactivates the user's account."""
        if self.active:
            current_app.logger.info(f"User {self.email} attempted to activate an already active account.")
            raise ValueError("Account is already active.")
        self.active = True
        self.reactivated_at = datetime.utcnow()
        db.session.commit()
        current_app.logger.info(f"User {self.email} reactivated their account.")

    ### Email Verification & Password Reset

    def get_reset_token(self, expires_sec=1800):
        """Generates a token for password resets that expires after a set time."""
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """Verifies the password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def generate_confirmation_token(self, expires_sec=3600):
        """Generates a token for confirming the user's email."""
        try:
            s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
            token = s.dumps({'confirm': self.id}).decode('utf-8')
            current_app.logger.info(f"Generated email confirmation token for user {self.email}")
            return token
        except Exception as e:
            current_app.logger.error(f"Error generating confirmation token for user {self.email}: {str(e)}")
            raise

    def confirm_email(self, token):
        """Confirms the user's email by checking the token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            if data.get('confirm') != self.id:
                raise ValueError("Invalid token")
            self.confirmed = True
            db.session.commit()
            current_app.logger.info(f"User {self.email} confirmed their email.")
            return True
        except Exception as e:
            current_app.logger.error(f"Error confirming email for user {self.email}: {str(e)}")
            return False


    ### Role and Permissions

    def is_admin(self):
        """Checks if the user has admin privileges."""
        return self.role == 'admin'

    def promote_to_admin(self):
        """Promotes the user to admin."""
        self.role = 'admin'
        db.session.commit()

    def demote_to_user(self):
        """Demotes an admin user to a regular user."""
        if self.role == 'admin':
            self.role = 'user'
            db.session.commit()

    ### Static Methods

    @staticmethod
    def find_by_email(email):
        """Finds a user by their email address."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_username(username):
        """Finds a user by their username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create_user(email, username, password):
        """
        Creates a new user with validated email and username.
        Validates that the email and username are unique, and that the password meets complexity requirements.
        """
        try:
            # Validate email and username
            if not User.is_valid_email(email):
                current_app.logger.error(f"Attempt to register with invalid email: {email}")
                raise ValueError("Invalid email format.")
            if not User.is_valid_username(username):
                current_app.logger.error(f"Attempt to register with invalid username: {username}")
                raise ValueError("Invalid username.")
            
            # Check if the email or username is already taken
            if User.find_by_email(email):
                current_app.logger.warning(f"Email already registered: {email}")
                raise ValueError("Email is already registered.")
            if User.find_by_username(username):
                current_app.logger.warning(f"Username already taken: {username}")
                raise ValueError("Username is already taken.")
            
            # Create the new user
            new_user = User(email=email, username=username)
            new_user.set_password(password)  # Hash the password

            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f"New user created: {new_user.email}")
            return new_user
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error while creating user {email}: {str(e)}")
            raise ValueError("There was an error creating the user, please try again.")
        except Exception as e:
            current_app.logger.error(f"General error while creating user {email}: {str(e)}")
            raise ValueError(f"Unexpected error: {str(e)}")

    ### Validation Methods

    @staticmethod
    def validate_password(password):
        """
        Validates that the password meets the following complexity rules:
        - Minimum length: 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            current_app.logger.warning("Password does not meet length requirement")
            return False
        if not re.search(r"[A-Z]", password):
            current_app.logger.warning("Password does not have an uppercase letter")
            return False
        if not re.search(r"[a-z]", password):
            current_app.logger.warning("Password does not have a lowercase letter")
            return False
        if not re.search(r"\d", password):
            current_app.logger.warning("Password does not have a digit")
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            current_app.logger.warning("Password does not have a special character")
            return False
        return True

    @staticmethod
    def is_valid_email(email):
        """Validates if the provided email is in a correct format."""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            current_app.logger.warning(f"Invalid email format: {email}")
            return False
        return True

    @staticmethod
    def is_valid_username(username):
        """Validates if the username meets certain criteria."""
        if not re.match(r"^[a-zA-Z0-9]{4,}$", username):
            current_app.logger.warning(f"Invalid username format: {username}")
            return False
        return True

    # Adding a role relationship to the existing User model
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    role = db.relationship('Role', back_populates='users')

    # Example: Admin user creation
    def create_admin_user(username, email, password):
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role:
            raise Exception("Admin role not found.")
        user = User(username=username, email=email, role=admin_role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user