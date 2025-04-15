import requests
import json

# URL of the registration endpoint
url = "http://127.0.0.1:5000/registration_page_1"

# Form data for the first page of registration
data = {
    "personnel_number": "12345",
    "rank": "Captain",
    "name": "John Doe",
    "unit": "Unit A",
    "dob": "1990-01-01",
    "year_in_rank": "2020",
    "year_of_last_promotion": "2020"
}

# Send a POST request to the registration endpoint
response = requests.post(url, data=data)

# Print the response
print(f"Status code: {response.status_code}")
print(f"Response: {response.text[:100]}...")  # Print first 100 chars of response
