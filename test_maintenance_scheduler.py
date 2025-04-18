"""
Test script for the maintenance scheduler
"""

from nass_portal.maintenance_tasks import check_maintenance_schedule
from flask import Flask
import time

app = Flask(__name__)

with app.app_context():
    print("Testing maintenance scheduler...")
    print("Checking maintenance schedule...")
    check_maintenance_schedule()
    print("Done checking maintenance schedule.")
    print("Waiting 10 seconds before checking again...")
    time.sleep(10)
    print("Checking maintenance schedule again...")
    check_maintenance_schedule()
    print("Done checking maintenance schedule.")
    print("Test complete.")
