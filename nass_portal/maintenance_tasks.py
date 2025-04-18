"""
Background tasks for maintenance mode management
"""

import sqlite3
import logging
from datetime import datetime
import os
import time
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a database connection"""
    db_path = os.path.join('instance', 'nass_portal.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def update_setting(key, value):
    """Update a setting in the database"""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE settings SET setting_value = ? WHERE setting_key = ?',
            (value, key)
        )
        conn.commit()
        logger.info(f"Updated setting {key} to {value}")
        return True
    except Exception as e:
        logger.error(f"Error updating setting {key}: {str(e)}")
        return False
    finally:
        conn.close()

def check_maintenance_schedule():
    """
    Check if there are any scheduled maintenance periods that should be
    started or completed based on the current time
    """
    logger.info("Checking maintenance schedule...")

    try:
        conn = get_db_connection()

        # Get current time
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%dT%H:%M:%S')

        # Check if auto-enable is turned on
        auto_enable = conn.execute(
            'SELECT setting_value FROM settings WHERE setting_key = ?',
            ('maintenance_auto_enable',)
        ).fetchone()

        if not auto_enable or auto_enable['setting_value'].lower() != 'true':
            logger.info("Auto-enable maintenance is disabled")
            conn.close()
            return

        # Check for scheduled maintenance that should be started
        scheduled = conn.execute(
            'SELECT * FROM scheduled_maintenance WHERE status = ? AND start_datetime <= ? AND end_datetime > ?',
            ('scheduled', now_str, now_str)
        ).fetchall()

        if scheduled:
            # Start the first scheduled maintenance
            maintenance = scheduled[0]
            logger.info(f"Starting scheduled maintenance: {maintenance['title']}")

            # Update maintenance status
            conn.execute(
                'UPDATE scheduled_maintenance SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                ('in_progress', maintenance['id'])
            )

            # Enable maintenance mode - directly update the database
            conn.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', ('true', 'maintenance_mode'))

            # Update maintenance message
            update_setting('maintenance_message',
                          f"The system is currently undergoing scheduled maintenance: {maintenance['title']}. "
                          f"We expect to be back online by {maintenance['end_datetime'].replace('T', ' ')}.")

            conn.commit()
            logger.info(f"Maintenance mode enabled for: {maintenance['title']}")

        # Check for in-progress maintenance that should be completed
        in_progress = conn.execute(
            'SELECT * FROM scheduled_maintenance WHERE status = ? AND end_datetime <= ?',
            ('in_progress', now_str)
        ).fetchall()

        if in_progress:
            # Complete all expired maintenance
            for maintenance in in_progress:
                logger.info(f"Completing maintenance: {maintenance['title']}")

                # Update maintenance status
                conn.execute(
                    'UPDATE scheduled_maintenance SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    ('completed', maintenance['id'])
                )

            # Only disable maintenance mode if there are no other active maintenance periods
            active = conn.execute(
                'SELECT COUNT(*) as count FROM scheduled_maintenance WHERE status = ? AND end_datetime > ?',
                ('in_progress', now_str)
            ).fetchone()

            if active['count'] == 0:
                # Disable maintenance mode - directly update the database
                conn.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', ('false', 'maintenance_mode'))
                logger.info("All maintenance completed, maintenance mode disabled")

            conn.commit()

    except Exception as e:
        logger.error(f"Error checking maintenance schedule: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if 'conn' in locals():
            conn.close()

def maintenance_scheduler():
    """
    Background thread that periodically checks the maintenance schedule
    """
    logger.info("Starting maintenance scheduler thread")

    while True:
        try:
            check_maintenance_schedule()
        except Exception as e:
            logger.error(f"Error in maintenance scheduler: {str(e)}")

        # Sleep for 1 minute before checking again
        time.sleep(60)

def start_scheduler():
    """
    Start the maintenance scheduler in a background thread
    """
    scheduler_thread = threading.Thread(target=maintenance_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Maintenance scheduler started in background thread")
