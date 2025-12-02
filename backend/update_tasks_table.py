import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def update_tasks_table():
    print("Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Adding missing columns to tasks table...")
        cur.execute("""
            ALTER TABLE arms_workflow.tasks 
            ADD COLUMN IF NOT EXISTS target_qty INTEGER DEFAULT 1,
            ADD COLUMN IF NOT EXISTS achieved_qty INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS rating INTEGER,
            ADD COLUMN IF NOT EXISTS remarks TEXT,
            ADD COLUMN IF NOT EXISTS picked_at TIMESTAMP WITH TIME ZONE,
            ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE;
        """)
        
        conn.commit()
        print("Columns added successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_tasks_table()
