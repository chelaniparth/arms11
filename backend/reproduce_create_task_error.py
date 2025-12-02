import requests
import uuid

BASE_URL = "http://localhost:8000"

def reproduce():
    # 1. Login as admin to create 'parth' user if needed
    # Assuming admin credentials from seed data
    admin_email = "admin@example.com"
    admin_password = "admin" # Default seed password
    
    print("Logging in as admin...")
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": admin_email, "password": admin_password})
    if response.status_code != 200:
        print("Failed to login as admin")
        return
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Create 'parth' user
    parth_email = "parth@example.com"
    parth_password = "password123"
    
    print("Checking if 'parth' exists...")
    users = requests.get(f"{BASE_URL}/users/", headers=admin_headers).json()
    parth_user = next((u for u in users if u["email"] == parth_email), None)
    
    if not parth_user:
        print("Creating 'parth' user...")
        create_data = {
            "email": parth_email,
            "username": "parth",
            "full_name": "Parth Analyst",
            "password": parth_password,
            "role": "analyst",
            "is_active": True
        }
        resp = requests.post(f"{BASE_URL}/users/", json=create_data, headers=admin_headers)
        if resp.status_code == 200:
            parth_user = resp.json()
            print("Created 'parth' user.")
        else:
            print(f"Failed to create user: {resp.text}")
            return
    else:
        print("User 'parth' already exists. Resetting password...")
        # Reset password
        update_data = {"password": parth_password}
        resp = requests.put(f"{BASE_URL}/users/{parth_user['id']}", json=update_data, headers=admin_headers)
        if resp.status_code != 200:
            print(f"Failed to reset password: {resp.text}")
            return
        print("Password reset successfully.")
        
    # 3. Login as 'parth'
    print("Logging in as 'parth'...")
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": parth_email, "password": parth_password})
    if response.status_code != 200:
        print(f"Failed to login as parth: {response.text}")
        return
    parth_token = response.json()["access_token"]
    parth_headers = {"Authorization": f"Bearer {parth_token}"}
    
    # 4. Try to create a task (Unassigned)
    print("Attempting to create UNASSIGNED task as 'parth'...")
    task_data_unassigned = {
        "company_name": "Test Company Unassigned",
        "document_type": "10Q",
        "task_type": "Tier I",
        "priority": "Medium",
        "target_qty": 1,
        "achieved_qty": 0,
        "assigned_user_id": None, 
        "description": "Test unassigned task created by parth"
    }
    
    resp = requests.post(f"{BASE_URL}/tasks/", json=task_data_unassigned, headers=parth_headers)
    if resp.status_code == 200:
        print("Unassigned Task created successfully!")
    else:
        print(f"Failed to create unassigned task: {resp.status_code}")
        print(resp.text)

    # 5. Try to create a task with Workflow
    print("Fetching workflows as 'parth'...")
    wf_resp = requests.get(f"{BASE_URL}/workflows/", headers=parth_headers)
    if wf_resp.status_code == 200:
        workflows = wf_resp.json()
        if workflows:
            wf_id = workflows[0]['config_id']
            print(f"Found workflow ID: {wf_id}. Creating task with workflow...")
            
            task_data_wf = {
                "company_name": "Test Company Workflow",
                "document_type": "10Q",
                "task_type": "Tier I",
                "priority": "Medium",
                "target_qty": 1,
                "achieved_qty": 0,
                "assigned_user_id": parth_user["id"],
                "workflow_config_id": wf_id,
                "description": "Test workflow task created by parth"
            }
            
            resp = requests.post(f"{BASE_URL}/tasks/", json=task_data_wf, headers=parth_headers)
            if resp.status_code == 200:
                print("Workflow Task created successfully!")
            else:
                print(f"Failed to create workflow task: {resp.status_code}")
                print(resp.text)
        else:
            print("No workflows found.")
    else:
        print(f"Failed to fetch workflows: {wf_resp.status_code}")

if __name__ == "__main__":
    reproduce()
