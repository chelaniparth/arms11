import requests
import sys

BASE_URL = "http://localhost:8000"

def test_export():
    # 1. Login
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Export
        print("Requesting export...")
        response = requests.get(f"{BASE_URL}/tasks/export", headers=headers)
        
        if response.status_code == 200:
            print("Export successful!")
            content = response.text
            line_count = len(content.splitlines())
            print(f"Received {line_count} lines of CSV data.")
            print("First 3 lines:")
            print("\n".join(content.splitlines()[:3]))
            
            if "Task ID,Company,Type" in content or "Task ID" in content:
                print("Header verification: PASSED")
            else:
                print("Header verification: FAILED")
        else:
            print(f"Export failed: {response.status_code} {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_export()
