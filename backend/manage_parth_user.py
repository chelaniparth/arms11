import psycopg2
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def manage_parth_user():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT id, username FROM arms_workflow.users WHERE username = 'parth'")
        user = cur.fetchone()
        
        password_hash = pwd_context.hash("admin")
        
        if user:
            print(f"User 'parth' exists (ID: {user[0]}). Updating password...")
            cur.execute(
                "UPDATE arms_workflow.users SET password_hash = %s WHERE username = 'parth'",
                (password_hash,)
            )
        else:
            print("User 'parth' does not exist. Creating...")
            cur.execute(
                """
                INSERT INTO arms_workflow.users (username, email, full_name, role, password_hash)
                VALUES ('parth', 'parth@arms.com', 'Parth Chelani', 'analyst', %s)
                """,
                (password_hash,)
            )
            
        conn.commit()
        print("User 'parth' setup complete with password 'admin'.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    manage_parth_user()
