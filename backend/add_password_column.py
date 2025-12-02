import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def add_column():
    print("Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Adding password_hash column...")
        cur.execute("""
            ALTER TABLE arms_workflow.users 
            ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);
        """)
        
        conn.commit()
        print("Column added successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    add_column()
