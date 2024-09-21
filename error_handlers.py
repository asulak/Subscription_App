# error_handlers.py

from flask import jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register global error handlers for the Flask application."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle HTTP errors (e.g., 404, 403)."""
        response = jsonify({
            'error': error.name,
            'description': error.description,
            'status_code': error.code
        })
        return response, error.code

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """Handle database integrity errors (e.g., unique constraint violations)."""
        response = jsonify({
            'error': 'Database Error',
            'description': 'A database integrity error occurred.',
            'details': str(error.orig)
        })
        return response, 400

    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle general exceptions."""
        response = jsonify({
            'error': 'Internal Server Error',
            'description': 'An unexpected error occurred.',
            'details': str(error)  # Optional: Remove in production to avoid leaking sensitive information
        })
        return response, 500
