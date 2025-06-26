@echo off
REM Run the NASS Portal application in production mode

REM Set environment variables
set FLASK_ENV=production

REM Run the application
python run.py

REM Pause to see any errors
pause
