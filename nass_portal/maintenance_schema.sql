-- Add scheduled maintenance table
CREATE TABLE IF NOT EXISTS scheduled_maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    start_datetime TEXT NOT NULL,  -- ISO format: YYYY-MM-DDTHH:MM:SS
    end_datetime TEXT NOT NULL,    -- ISO format: YYYY-MM-DDTHH:MM:SS
    status TEXT NOT NULL DEFAULT 'scheduled',  -- 'scheduled', 'in_progress', 'completed', 'cancelled'
    notification_days_before INTEGER NOT NULL DEFAULT 3,  -- Days before to start showing notification
    show_countdown BOOLEAN NOT NULL DEFAULT 1,  -- Whether to show countdown timer
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Add maintenance notifications table for users who want to be notified
CREATE TABLE IF NOT EXISTS maintenance_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    maintenance_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    notification_sent BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maintenance_id) REFERENCES scheduled_maintenance (id) ON DELETE CASCADE
);

-- Add settings for maintenance mode
INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type, category, description, is_public)
VALUES 
('maintenance_auto_enable', 'true', 'boolean', 'maintenance', 'Automatically enable maintenance mode based on schedule', 0),
('maintenance_notification_enabled', 'true', 'boolean', 'maintenance', 'Show maintenance notifications to users', 1),
('maintenance_notification_style', 'banner', 'text', 'maintenance', 'Style of maintenance notification (banner, popup, subtle)', 1),
('maintenance_contact_email', '', 'text', 'maintenance', 'Contact email to display during maintenance', 1),
('maintenance_contact_phone', '', 'text', 'maintenance', 'Contact phone to display during maintenance', 1);
