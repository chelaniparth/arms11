import requests
import json

BASE_URL = "http://localhost:8000"

def reproduce():
    # 1. Login as 'parth'
    print("Logging in as 'parth'...")
    login_data = {
        "username": "parth",
        "password": "password123"
    }
    
    resp = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if resp.status_code != 200:
        print(f"Failed to login as parth: {resp.text}")
        return
        
    parth_token = resp.json()["access_token"]
    parth_headers = {"Authorization": f"Bearer {parth_token}"}
    
    # 2. Create a task to complete
    print("Creating a task to complete...")
    task_data = {
        "company_name": "Test Completion Company",
        "document_type": "10Q",
        "task_type": "Tier I",
        "priority": "Medium",
        "target_qty": 1,
        "achieved_qty": 0,
        "assigned_user_id": None, # Will pick it up
        "description": "Task to test completion"
    }
    
    resp = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=parth_headers)
    if resp.status_code != 200:
        print(f"Failed to create task: {resp.text}")
        return
    task = resp.json()
    task_id = task['task_id']
    print(f"Task created: {task_id}")
    
    # 3. Pick up the task
    print("Picking up task...")
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/pick", headers=parth_headers)
    if resp.status_code != 200:
        print(f"Failed to pick task: {resp.text}")
        return
    print("Task picked up.")
    
    # 4. Complete the task
    print("Completing task...")
    update_data = {
        "achieved_qty": 1,
        "remarks": "Completed by Parth"
    }
    
    resp = requests.post(f"{BASE_URL}/tasks/{task_id}/complete", json=update_data, headers=parth_headers)
    if resp.status_code == 200:
        print("Task completed successfully!")
    else:
        print(f"Failed to complete task: {resp.status_code}")
        print(resp.text)

if __name__ == "__main__":
    reproduce()
