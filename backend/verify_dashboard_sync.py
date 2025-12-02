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

def get_my_stats(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
    if response.status_code == 200:
        return response.json()["my_stats"]
    else:
        print(f"Failed to get stats: {response.text}")
        return None

def create_task(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "task_type": "Tier I",
        "company_name": "Test Company Sync",
        "document_type": "Test Doc",
        "priority": "Medium",
        "target_qty": 1
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to create task: {response.text}")
        return None

def pick_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/tasks/{task_id}/pick", headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(f"Failed to pick task: {response.text}")
        return False

def delete_task(token, task_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}", headers=headers)
    if response.status_code == 200:
        return True
    else:
        print(f"Failed to delete task: {response.text}")
        return False

def main():
    print("1. Logging in as admin...")
    token = login("admin", "admin")
    if not token: return

    print("2. Getting initial stats...")
    initial_stats = get_my_stats(token)
    print(f"Initial In Progress: {initial_stats['tasks_in_progress']}")

    print("3. Creating a new task...")
    task = create_task(token)
    if not task: return
    task_id = task["task_id"]
    print(f"Task created with ID: {task_id}")

    print("4. Picking up the task...")
    if pick_task(token, task_id):
        print("Task picked up.")
    else:
        return

    print("5. Checking stats after pick up...")
    after_pick_stats = get_my_stats(token)
    print(f"After Pick In Progress: {after_pick_stats['tasks_in_progress']}")
    
    if after_pick_stats['tasks_in_progress'] != initial_stats['tasks_in_progress'] + 1:
        print("ERROR: In Progress count did not increment!")
    else:
        print("SUCCESS: In Progress count incremented.")

    print("6. Deleting the task...")
    if delete_task(token, task_id):
        print("Task deleted.")
    else:
        return

    print("7. Checking stats after delete...")
    final_stats = get_my_stats(token)
    print(f"Final In Progress: {final_stats['tasks_in_progress']}")

    if final_stats['tasks_in_progress'] != initial_stats['tasks_in_progress']:
        print("ERROR: In Progress count did not decrement back to initial!")
    else:
        print("SUCCESS: In Progress count decremented correctly.")

if __name__ == "__main__":
    main()
