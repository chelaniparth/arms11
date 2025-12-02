import psycopg2
import os
from dotenv import load_dotenv
import security

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def create_users():
    print("Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Creating admin user...")
        # Admin
        admin_pass = security.get_password_hash("admin")
        cur.execute("""
            INSERT INTO arms_workflow.users (username, email, full_name, role, password_hash, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, ("admin", "admin@example.com", "System Administrator", "admin", admin_pass, True))
        
        print("Creating other users...")
        # Other users
        users = [
            ("jen", "jen@example.com", "Jen", "manager"),
            ("komal", "komal@example.com", "Komal", "analyst"),
            ("parth", "parth@example.com", "Parth", "analyst"),
            ("prerna", "prerna@example.com", "Prerna", "analyst")
        ]
        
        default_pass = security.get_password_hash("password123")
        
        for u in users:
            cur.execute("""
                INSERT INTO arms_workflow.users (username, email, full_name, role, password_hash, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (u[0], u[1], u[2], u[3], default_pass, True))
            
        conn.commit()
        print("Users created successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_users()
