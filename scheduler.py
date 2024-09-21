# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from services.invoice_reminder_service import send_reminders_for_unpaid_invoices
from app import create_app

def start_scheduler():
    """Start the background scheduler for sending reminders."""
    app = create_app()
    scheduler = BackgroundScheduler()
    
    # Schedule the reminder function to run every day at midnight
    scheduler.add_job(send_reminders_for_unpaid_invoices, 'interval', days=1, id='send_reminders', replace_existing=True)
    
    # Start the scheduler
    scheduler.start()

    # Keep the application running to listen for the scheduled tasks
    try:
        print("Scheduler started, running with application...")
        app.run(use_reloader=False)
    except KeyboardInterrupt:
        print("Scheduler shut down!")
        scheduler.shutdown()
