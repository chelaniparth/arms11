import requests
import sys

try:
    response = requests.post(
        "http://localhost:8000/auth/token",
        data={"username": "admin@arms.com", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        print("Success: Got token")
        print(response.json())
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
