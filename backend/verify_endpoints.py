import requests
import time

def verify():
    base_url = "http://localhost:8000"
    print("Waiting for server to start...")
    time.sleep(5)
    
    # 1. Test Workflows List
    try:
        print("Testing GET /workflows/ ...")
        res = requests.get(f"{base_url}/workflows/")
        if res.status_code == 200:
            print(f"SUCCESS: Found {len(res.json())} workflows.")
        else:
            print(f"FAILED: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"ERROR: {e}")

    # 2. Test Volume Endpoint
    try:
        print("Testing GET /workflows/volume ...")
        res = requests.get(f"{base_url}/workflows/volume")
        if res.status_code == 200:
            print(f"SUCCESS: Volume endpoint working. Data: {res.json()}")
        else:
            print(f"FAILED: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify()
