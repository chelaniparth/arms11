import psycopg2
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_login():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("SELECT password_hash FROM arms_workflow.users WHERE username = 'parth'")
        result = cur.fetchone()
        
        if result:
            stored_hash = result[0]
            print(f"Stored Hash: {stored_hash}")
            
            is_valid = pwd_context.verify("admin", stored_hash)
            print(f"Password 'admin' is valid: {is_valid}")
            
            if is_valid:
                print("SUCCESS: Login verification passed.")
            else:
                print("FAILURE: Login verification failed.")
        else:
            print("User 'parth' not found.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_login()
