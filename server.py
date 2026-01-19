#!/usr/bin/env python3
"""
Production server with scheduled notifications.
Deploy this to Railway, Render, or any cloud platform.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from notifications import send_notifications
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

def init_scheduler():
    """Initialize the notification scheduler."""
    scheduler = BackgroundScheduler()
    
    # Get notification time from environment
    notification_time = os.getenv('NOTIFICATION_TIME', '18:00')
    timezone = os.getenv('TIMEZONE', 'Asia/Shanghai')
    
    try:
        hour, minute = map(int, notification_time.split(':'))
        tz = pytz.timezone(timezone)
        
        # Schedule daily notification
        scheduler.add_job(
            send_notifications,
            CronTrigger(hour=hour, minute=minute, timezone=tz),
            id='daily_notification',
            name='Send daily breakfast notification',
            replace_existing=True
        )
        
        scheduler.start()
        print(f"📅 Scheduler started! Notifications at {notification_time} ({timezone})")
        
    except Exception as e:
        print(f"⚠️ Failed to start scheduler: {e}")
        print("Notifications will need to be sent manually.")


def init_database():
    """Initialize database if it doesn't exist."""
    db_path = os.path.join(os.path.dirname(__file__), 'breakfast.db')
    
    if not os.path.exists(db_path):
        print("📦 Database not found. Initializing...")
        from init_db import main as init_db_main
        init_db_main()


if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start scheduler
    init_scheduler()
    
    # Get port from environment (for cloud deployment)
    port = int(os.getenv('PORT', 5000))
    
    print(f"🍳 Starting Breakfast Decision System on port {port}")
    print("📍 Open http://localhost:{} in your browser".format(port))
    
    # Run with gunicorn in production, flask in development
    if os.getenv('PRODUCTION'):
        # Production mode - use gunicorn
        import gunicorn.app.base
        
        class StandaloneApplication(gunicorn.app.base.BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    if key in self.cfg.settings and value is not None:
                        self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        options = {
            'bind': f'0.0.0.0:{port}',
            'workers': 2,
        }
        StandaloneApplication(app, options).run()
    else:
        # Development mode
        app.run(debug=True, port=port, host='0.0.0.0')
