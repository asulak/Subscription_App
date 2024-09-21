"""
app.py File Purpose

1) Acts as the entry point to run your Flask application 
2) Creates an app instance - so where it is created and run
3) Runs the app  
    
"""

from app import create_app  # Import the application factory function

# Create app instance, specify configuration in parentheses
app = create_app()

# Runs app 
if __name__ == "__main__":
    app.run(debug=True)
