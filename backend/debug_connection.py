from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def debug_connection():
    print(f"--- Application Connection Details ---")
    print(f"URL: {DATABASE_URL}")
    
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            print("\n--- Database Server Info ---")
            # Get server info
            server_info = conn.execute(text("SELECT inet_server_addr(), inet_server_port(), current_database(), current_user, version();")).fetchone()
            print(f"Server IP: {server_info[0]}")
            print(f"Server Port: {server_info[1]}")
            print(f"Database Name: {server_info[2]}")
            print(f"Current User: {server_info[3]}")
            print(f"Version: {server_info[4]}")
            
            print("\n--- Date & Time Settings ---")
            time_info = conn.execute(text("SELECT CURRENT_DATE, NOW(), current_setting('TIMEZONE');")).fetchone()
            print(f"DB Current Date: {time_info[0]}")
            print(f"DB Now: {time_info[1]}")
            print(f"DB Timezone: {time_info[2]}")
            
            print("\n--- Data Check ---")
            # Check total tasks
            total_tasks = conn.execute(text("SELECT COUNT(*) FROM arms_workflow.tasks")).scalar()
            print(f"Total Tasks in DB: {total_tasks}")
            
            # Check completed tasks for parth
            sql = text("""
                SELECT COUNT(*) 
                FROM arms_workflow.tasks t
                JOIN arms_workflow.users u ON t.assigned_user_id = u.id
                WHERE u.username = 'parth'
                  AND t.status = 'Completed'
            """)
            completed_total = conn.execute(sql).scalar()
            print(f"Total Completed Tasks for Parth (All Time): {completed_total}")
            
            # Check completed tasks for parth TODAY
            sql_today = text("""
                SELECT COUNT(*) 
                FROM arms_workflow.tasks t
                JOIN arms_workflow.users u ON t.assigned_user_id = u.id
                WHERE u.username = 'parth'
                  AND t.status = 'Completed'
                  AND DATE(t.completed_at) = CURRENT_DATE
            """)
            completed_today = conn.execute(sql_today).scalar()
            print(f"Completed Tasks for Parth (Today): {completed_today}")
            
            if completed_today > 0:
                print("\n--- Sample Task Data ---")
                sample = conn.execute(text("""
                    SELECT t.task_id, t.company_name, t.completed_at 
                    FROM arms_workflow.tasks t
                    JOIN arms_workflow.users u ON t.assigned_user_id = u.id
                    WHERE u.username = 'parth' AND t.status = 'Completed'
                    LIMIT 3
                """)).fetchall()
                for row in sample:
                    print(f"ID: {row[0]}, Company: {row[1]}, Completed At: {row[2]}")

    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    debug_connection()
