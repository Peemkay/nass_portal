# PythonAnywhere Deployment Guide

This guide provides instructions for updating your NASS Portal deployment on PythonAnywhere.

## Prerequisites

- Your application is already deployed on PythonAnywhere
- Your code is hosted on GitHub
- Your PythonAnywhere account has access to your GitHub repository

## Updating Your Deployment

### Step 1: Log in to PythonAnywhere

1. Go to [PythonAnywhere](https://www.pythonanywhere.com/) and log in to your account.
2. Navigate to the "Consoles" tab and start a new Bash console.

### Step 2: Pull the Latest Changes

Run the following commands in the Bash console:

```bash
# Navigate to your project directory
cd ~/nass_portal

# Make sure you're on the main branch
git checkout main

# Pull the latest changes from GitHub
git pull
```

### Step 3: Update Database Schema (if needed)

If you've made changes to the database schema, you'll need to apply those changes:

```bash
# Apply maintenance schema
python apply_maintenance_schema.py
```

### Step 4: Restart the Web Application

To restart your web application, you can either:

1. Touch the WSGI file:
```bash
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

2. Or go to the "Web" tab in the PythonAnywhere dashboard and click the "Reload" button for your web app.

### Step 5: Check for Errors

If you encounter any issues, check the error log:

```bash
cat /var/log/yourusername.pythonanywhere.com.error.log
```

## Troubleshooting

### Git Pull Issues

If you encounter issues with `git pull`, make sure:
- Your repository is properly configured
- You have the correct permissions
- There are no conflicts with local changes

Try running:
```bash
git status
```

If there are local changes, you may need to stash them:
```bash
git stash
git pull
git stash pop
```

### Database Issues

If you encounter database issues:
- Check that your database path is correct in your configuration
- Ensure you have the necessary permissions
- Make a backup of your database before making schema changes

### WSGI Reload Issues

If your application doesn't update after touching the WSGI file:
- Check the error logs
- Make sure your WSGI file path is correct
- Try manually reloading from the Web tab

## Maintenance Mode

The maintenance mode feature allows you to put the site into maintenance mode while you're updating it. To enable maintenance mode:

1. Log in to the admin dashboard
2. Go to the Maintenance section
3. Create a new maintenance period or set an existing one to "in progress"

Alternatively, you can visit `/enable-maintenance` when logged in as an admin.

To disable maintenance mode after your update is complete, visit `/disable-maintenance` or update the maintenance period status in the admin dashboard.
