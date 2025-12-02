import requests

BASE_URL = "http://localhost:8000"

def check_and_reset():
    # 1. Login as admin
    print("Logging in as admin...")
    admin_email = "admin@example.com"
    admin_password = "admin"
    
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": admin_email, "password": admin_password})
    if resp.status_code != 200:
        print("Failed to login as admin")
        return
        
    admin_token = resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Search for user 'Nisrag'
    print("Searching for user 'Nisrag'...")
    resp = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    if resp.status_code != 200:
        print(f"Failed to fetch users: {resp.text}")
        return
        
    users = resp.json()
    # Look for Nisrag specifically
    nisarg_user = next((u for u in users if "nisrag" in u["username"].lower()), None)
    
    if nisarg_user:
        print(f"Found user: {nisarg_user['username']} ({nisarg_user['full_name']})")
        
        # 3. Reset password
        new_password = "password123"
        print(f"Resetting password to '{new_password}'...")
        
        update_data = {"password": new_password}
        resp = requests.put(f"{BASE_URL}/users/{nisarg_user['id']}", json=update_data, headers=admin_headers)
        
        if resp.status_code == 200:
            print("Password reset successfully.")
        else:
            print(f"Failed to reset password: {resp.status_code} - {resp.text}")
            
    else:
        print("User 'nisarg' not found. Listing all users:")
        for u in users:
            print(f"- {u['username']} ({u['full_name']})")

if __name__ == "__main__":
    check_and_reset()
