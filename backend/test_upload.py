import requests
import os

# Login to get token
def get_token():
    try:
        response = requests.post(
            "http://localhost:8000/auth/token",
            data={"username": "admin", "password": "admin"}, # Assuming admin user exists
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except Exception as e:
        print(f"Login failed: {e}")
        try:
            print(response.json())
        except:
            print(response.text)
        return None

def test_upload():
    token = get_token()
    if not token:
        return

    # Create a dummy CSV file
    csv_content = """company_name,document_type,task_type,priority,description,notes
Test Company,Invoice,Data Entry,High,Test Description,Test Note
"""
    with open("test_upload.csv", "w") as f:
        f.write(csv_content)

    try:
        with open("test_upload.csv", "rb") as f:
            files = {"file": ("test_upload.csv", f, "text/csv")}
            headers = {"Authorization": f"Bearer {token}"}
            
            print("Attempting upload...")
            response = requests.post(
                "http://localhost:8000/tasks/upload",
                headers=headers,
                files=files
            )
            
            print(f"Status Code: {response.status_code}")
            try:
                print("Response JSON:", response.json())
            except:
                print("Response Text:", response.text)
                
    except Exception as e:
        print(f"Upload failed: {e}")
    finally:
        if os.path.exists("test_upload.csv"):
            os.remove("test_upload.csv")

if __name__ == "__main__":
    test_upload()
