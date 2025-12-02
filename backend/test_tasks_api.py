import requests
import json

def get_token():
    try:
        response = requests.post(
            "http://localhost:8000/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        return None

def test_get_tasks():
    token = get_token()
    if not token:
        return

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8000/tasks", headers=headers)
        response.raise_for_status()
        
        tasks = response.json()
        print(f"Fetched {len(tasks)} tasks.")
        
        # Check for the recently created tasks (e.g. "BnL")
        found = False
        for task in tasks:
            if task['company_name'] == "BnL (Buy n Large)":
                print("Found task 'BnL (Buy n Large)' in API response.")
                found = True
                break
        
        if not found:
            print("Task 'BnL (Buy n Large)' NOT found in API response.")
            
    except Exception as e:
        print(f"API call failed: {e}")

if __name__ == "__main__":
    test_get_tasks()
