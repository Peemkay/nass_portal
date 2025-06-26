-- Impact Statistics Table
CREATE TABLE IF NOT EXISTS impact_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    value TEXT NOT NULL,
    icon TEXT,
    color TEXT DEFAULT 'primary',
    display_order INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default impact statistics
INSERT OR IGNORE INTO impact_stats (id, title, value, icon, color, display_order, active)
VALUES 
    (1, 'Courses Offered', '50+', 'fas fa-book', 'primary', 1, 1),
    (2, 'Graduates', '5,000+', 'fas fa-user-graduate', 'success', 2, 1),
    (3, 'Years of Excellence', '30+', 'fas fa-award', 'danger', 3, 1);
