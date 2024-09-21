from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from models.user import User
from app import db, mail

auth = Blueprint('auth', __name__)

### LOGIN ROUTE ###
@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find user by email
        user = User.find_by_email(email)
        
        # Verify user and check password
        if user and user.check_password(password):
            if not user.active:
                flash('Your account is inactive. Please contact support.', 'warning')
                return redirect(url_for('auth.login'))

            # Log the user in and update last login time
            login_user(user)
            user.mark_login()
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))

        # Invalid login attempt
        flash('Invalid email or password.', 'danger')
    
    # Render the login page for GET request or failed login
    return render_template('login.html')

### REGISTRATION ROUTE ###
@auth.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration."""
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        if User.find_by_email(email):
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))
        if User.find_by_username(username):
            flash('Username already taken.', 'danger')
            return redirect(url_for('auth.register'))

        # Create a new user and set the password
        new_user = User(email=email, username=username)
        try:
            new_user.set_password(password)  # Hash and store the password
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)  # Log the user in automatically after registration
            flash('Registration successful! Welcome, ' + username, 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration for {email}: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')

    # Render the registration page for GET request or failed registration
    return render_template('register.html')

### LOGOUT ROUTE ###
@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

### PASSWORD RESET REQUEST ROUTE ###
@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Send a password reset token to the user's email."""
    if request.method == 'POST':
        email = request.form['email']
        user = User.find_by_email(email)
        
        if user:
            send_reset_email(user)  # Call to send the reset email
            flash('A password reset link has been sent to your email.', 'info')
        else:
            flash('Email not found. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('reset_password_request.html')

### PASSWORD RESET ROUTE ###
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset the user's password using the token."""
    user = User.verify_reset_token(token)
    if not user:
        flash('The token is invalid or has expired.', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    if request.method == 'POST':
        password = request.form['password']
        try:
            user.set_password(password)  # Hash and update the password
            db.session.commit()
            flash('Your password has been updated! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating password for {user.email}: {str(e)}")
            flash('Error updating your password. Please try again.', 'danger')

    return render_template('reset_password.html', token=token)

### SEND RESET EMAIL FUNCTION ###
def send_reset_email(user):
    """
    Send a password reset email to the user with a unique reset token.

    Args:
        user (User): The user object for which the reset email should be sent.

    Returns:
        None
    """
    # Step 1: Generate a secure token for password reset
    token = user.get_reset_token()

    # Step 2: Construct the reset URL
    reset_link = url_for('auth.reset_password', token=token, _external=True)

    # Step 3: Compose the email
    msg = Message(
        'Password Reset Request',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email]
    )
    msg.body = f'''Dear {user.username},

We received a request to reset your password. If you made this request, you can reset your password by clicking the link below:

{reset_link}

If you did not request a password reset, please ignore this email and your password will remain unchanged.

This link will expire in 30 minutes for your security.

Thank you,
The Support Team
'''

    # Step 4: Send the email
    try:
        mail.send(msg)
        current_app.logger.info(f"Password reset email sent to {user.email}.")
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")

def admin_required(f):
    """Decorator to ensure user has admin role."""
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role.name != 'admin':
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@auth.route('/admin-only', methods=['GET'])
@login_required
@admin_required
def admin_only_route():
    """Example of a route restricted to admins."""
    return jsonify({'message': 'Welcome, Admin!'})