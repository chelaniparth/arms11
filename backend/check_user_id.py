import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_user():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        user_id = 'b00855f8-be4d-4897-aaac-ce31ecf9876e'
        cur.execute("SELECT username, role, full_name FROM arms_workflow.users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        
        if user:
            print(f"User Found: Username={user[0]}, Role={user[1]}, Name={user[2]}")
        else:
            print("User not found.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    check_user()
