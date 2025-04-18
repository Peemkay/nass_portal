from flask import request, session, current_app, g, render_template
from datetime import datetime, timedelta

def check_maintenance_mode():
    """
    Middleware to check if the site is in maintenance mode.
    If it is, redirect non-admin users to a maintenance page.
    Also handles showing notifications for upcoming maintenance.
    """
    try:
        current_app.logger.info(f"Checking maintenance mode for path: {request.path}")

        # Skip maintenance check for maintenance route itself
        if request.path == '/maintenance':
            current_app.logger.info(f"Skipping maintenance check for maintenance page itself")
            return None

        # Skip maintenance check for enable/disable maintenance routes
        if request.path == '/enable-maintenance' or request.path == '/disable-maintenance':
            current_app.logger.info(f"Skipping maintenance check for maintenance control routes")
            return None

        # Skip maintenance check for admin routes and static files
        if request.path.startswith('/admin') or request.path.startswith('/static'):
            current_app.logger.info(f"Skipping maintenance check for admin/static path: {request.path}")
            return None

        # Check if maintenance mode is enabled - directly query the database
        from .db import get_db

        db = get_db()
        setting = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_mode',)).fetchone()

        maintenance_mode = False
        if setting and setting['setting_value'].lower() == 'true':
            maintenance_mode = True
            current_app.logger.info(f"Maintenance mode is ENABLED")
        else:
            current_app.logger.info(f"Maintenance mode is DISABLED")

        # Check for in-progress maintenance
        in_progress = db.execute('SELECT COUNT(*) as count FROM scheduled_maintenance WHERE status = "in_progress"').fetchone()
        current_app.logger.info(f"In-progress maintenance count: {in_progress['count'] if in_progress else 0}")

        # If there's in-progress maintenance but maintenance mode is not enabled, enable it
        if in_progress and in_progress['count'] > 0 and not maintenance_mode:
            current_app.logger.info(f"In-progress maintenance detected, enabling maintenance mode")
            db.execute('UPDATE settings SET setting_value = ? WHERE setting_key = ?', ('true', 'maintenance_mode'))
            db.commit()
            maintenance_mode = True

        # Debug log
        current_app.logger.info(f"Maintenance mode setting value (direct DB): {maintenance_mode}")

        # Allow admin users to bypass maintenance mode
        if maintenance_mode and session.get('admin_logged_in') == True:
            current_app.logger.info(f"Admin user bypassing maintenance mode")
            return None

        if maintenance_mode:
            # Get maintenance message and contact information
            message_setting = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_message',)).fetchone()
            maintenance_message = 'The system is currently undergoing scheduled maintenance. Please check back later.'

            if message_setting:
                maintenance_message = message_setting['setting_value']

            # Get contact information
            contact_email = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_contact_email',)).fetchone()
            contact_phone = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?', ('maintenance_contact_phone',)).fetchone()

            # Get active maintenance details if available
            active_maintenance = db.execute(
                'SELECT * FROM scheduled_maintenance WHERE status = "in_progress" ORDER BY start_datetime LIMIT 1'
            ).fetchone()

            # Log that we're showing maintenance mode
            current_app.logger.info(f"Showing maintenance mode page to user. Path: {request.path}")

            # No need to import render_template again

            # Return maintenance page with all available information
            return render_template('maintenance.html',
                                  message=maintenance_message,
                                  contact_email=contact_email['setting_value'] if contact_email else None,
                                  contact_phone=contact_phone['setting_value'] if contact_phone else None,
                                  maintenance=active_maintenance)
        else:
            # Check for upcoming maintenance to show notification
            # Only if we're not already in maintenance mode
            try:
                # Store upcoming maintenance info in g for templates to access
                g.upcoming_maintenance = None
                g.show_maintenance_notification = False

                # Check if notifications are enabled
                notification_enabled = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?',
                                                ('maintenance_notification_enabled',)).fetchone()

                if notification_enabled and notification_enabled['setting_value'].lower() == 'true':
                    # Get current date
                    now = datetime.now()

                    # Find the next scheduled maintenance
                    upcoming = db.execute(
                        'SELECT * FROM scheduled_maintenance WHERE status = "scheduled" AND start_datetime > ? ORDER BY start_datetime LIMIT 1',
                        (now.strftime('%Y-%m-%dT%H:%M:%S'),)
                    ).fetchone()

                    if upcoming:
                        # Parse the start datetime
                        start_dt = datetime.fromisoformat(upcoming['start_datetime'])

                        # Check if we're within the notification period
                        notification_days = upcoming['notification_days_before']
                        notification_start = start_dt - timedelta(days=notification_days)

                        if now >= notification_start:
                            # We should show a notification
                            g.upcoming_maintenance = upcoming
                            g.show_maintenance_notification = True

                            # Get notification style
                            style_setting = db.execute('SELECT setting_value FROM settings WHERE setting_key = ?',
                                                     ('maintenance_notification_style',)).fetchone()
                            g.notification_style = style_setting['setting_value'] if style_setting else 'banner'
            except Exception as e:
                current_app.logger.error(f"Error checking for upcoming maintenance: {str(e)}")
                # Don't let notification errors break the site
                g.show_maintenance_notification = False

            current_app.logger.info(f"Maintenance mode is disabled, continuing normal request")
    except Exception as e:
        # Log any errors that occur during maintenance mode check
        current_app.logger.error(f"Error checking maintenance mode: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())

    return None
