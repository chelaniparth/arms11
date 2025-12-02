import urllib.request
import urllib.parse
import json
import sys

url = "http://localhost:8000/auth/token"
data = urllib.parse.urlencode({"username": "admin@arms.com", "password": "admin123"}).encode()
req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})

try:
    with urllib.request.urlopen(req) as response:
        if response.status == 200:
            print("Success: Got token")
            print(response.read().decode())
        else:
            print(f"Failed: {response.status}")
            sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
