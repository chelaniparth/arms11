import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("1. Logging in...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "admin", "password": "admin"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")
    except Exception as e:
        print(f"Could not connect to backend: {e}")
        return

    print("\n2. Creating Task...")
    task_data = {
        "company_name": "Test Company API",
        "document_type": "10-K",
        "task_type": "Tier I",
        "priority": "Medium",
        "target_qty": 1,
        "achieved_qty": 0
    }
    resp = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    if resp.status_code != 200:
        print(f"Create task failed: {resp.text}")
        return
    task = resp.json()
    task_id = task["task_id"]
    print(f"Task created: ID {task_id}")

    print("\n3. Picking Task...")
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/pick", headers=headers)
    if resp.status_code != 200:
        print(f"Pick task failed: {resp.text}")
    else:
        print("Pick task successful.")

    print("\n4. Updating Task (Assignment)...")
    # Create another task for update test
    resp = requests.post(f"{BASE_URL}/tasks/", json={**task_data, "company_name": "Test Update API"}, headers=headers)
    task2_id = resp.json()["task_id"]
    
    update_data = {
        "status": "In Progress",
        "assigned_user_id": None # Test unassigning or just updating status
    }
    resp = requests.put(f"{BASE_URL}/tasks/{task2_id}", json=update_data, headers=headers)
    if resp.status_code != 200:
        print(f"Update task failed: {resp.text}")
    else:
        print("Update task successful.")

if __name__ == "__main__":
    test_api()
