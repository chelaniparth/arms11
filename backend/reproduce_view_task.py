import requests
import json

BASE_URL = "http://localhost:8000"

def reproduce():
    # 1. Login as 'parth'
    print("Logging in as 'parth'...")
    login_data = {
        "username": "parth",
        "password": "password123" # Assuming this was the reset password
    }
    
    resp = requests.post(f"{BASE_URL}/auth/token", data=login_data)
    if resp.status_code != 200:
        print(f"Failed to login as parth: {resp.text}")
        return
        
    parth_token = resp.json()["access_token"]
    parth_headers = {"Authorization": f"Bearer {parth_token}"}
    
    # 2. Get list of tasks to find one created by parth
    print("Fetching tasks...")
    resp = requests.get(f"{BASE_URL}/tasks/", headers=parth_headers)
    if resp.status_code != 200:
        print(f"Failed to fetch tasks: {resp.text}")
        return
        
    tasks = resp.json()
    if not tasks:
        print("No tasks found.")
        return
        
    # Pick the first task
    task_id = tasks[0]['task_id']
    print(f"Found task ID: {task_id}")
    
    # 3. Fetch task details
    print(f"Fetching details for task {task_id}...")
    try:
        resp = requests.get(f"{BASE_URL}/tasks/{task_id}", headers=parth_headers)
        if resp.status_code == 200:
            print("Task details fetched successfully!")
        else:
            print(f"Failed to fetch task details: {resp.status_code} - {resp.text}")

        # 4. Fetch comments
        print(f"Fetching comments for task {task_id}...")
        resp = requests.get(f"{BASE_URL}/tasks/{task_id}/comments", headers=parth_headers)
        if resp.status_code == 200:
            print("Comments fetched successfully!")
        else:
            print(f"Failed to fetch comments: {resp.status_code} - {resp.text}")

        # 5. Fetch history
        print(f"Fetching history for task {task_id}...")
        resp = requests.get(f"{BASE_URL}/tasks/{task_id}/history", headers=parth_headers)
        if resp.status_code == 200:
            print("History fetched successfully!")
        else:
            print(f"Failed to fetch history: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"Exception during requests: {e}")

if __name__ == "__main__":
    reproduce()
