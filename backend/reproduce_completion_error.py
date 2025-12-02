import requests
import json

BASE_URL = "http://localhost:8000"

def login(username, password):
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def create_task(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "task_type": "Tier I",
        "company_name": "Test Completion",
        "document_type": "Test Doc",
        "priority": "Medium",
        "target_qty": 1,
        "status": "In Progress" # Create as In Progress so we can complete it
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create task: {response.text}")
        return None

def complete_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "status": "Completed",
        "achieved_qty": 1,
        "remarks": "Done via script"
    }
    response = requests.put(f"{BASE_URL}/tasks/{task_id}", json=data, headers=headers)
    if response.status_code == 200:
        print("Task completed successfully.")
        return True
    else:
        print(f"Failed to complete task: {response.status_code} - {response.text}")
        return False

def main():
    print("1. Logging in...")
    token = login("admin", "admin")
    if not token: return

    print("2. Creating task...")
    task = create_task(token)
    if not task: return
    task_id = task["task_id"]
    print(f"Task created: {task_id}")

    print("3. Completing task...")
    complete_task(token, task_id)

if __name__ == "__main__":
    main()
