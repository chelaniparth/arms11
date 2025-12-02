import psycopg2
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_recent_tasks():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        print("Checking for tasks created in the last hour...")
        
        # Query tasks created recently
        cur.execute("""
            SELECT task_id, company_name, task_type, status, assigned_user_id, created_at 
            FROM arms_workflow.tasks 
            ORDER BY created_at DESC 
            LIMIT 10;
        """)
        
        tasks = cur.fetchall()
        
        if not tasks:
            print("No tasks found.")
        else:
            print(f"Found {len(tasks)} recent tasks:")
            for task in tasks:
                print(f"ID: {task[0]}, Company: {task[1]}, Type: {task[2]}, Status: {task[3]}, Assigned User: {task[4]}, Created: {task[5]}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    check_recent_tasks()
