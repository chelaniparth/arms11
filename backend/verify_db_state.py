from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def verify_connection_and_data():
    print(f"Connecting to: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Check DB name
            db_name = conn.execute(text("SELECT current_database();")).scalar()
            print(f"Connected to Database: {db_name}")
            
            # Check User
            user = conn.execute(text("SELECT current_user;")).scalar()
            print(f"Connected as User: {user}")
            
            # Check Count
            sql = text("""
                SELECT COUNT(*) 
                FROM arms_workflow.tasks t
                JOIN arms_workflow.users u ON t.assigned_user_id = u.id
                WHERE u.username = 'parth'
                  AND t.status = 'Completed'
                  AND DATE(t.completed_at) = CURRENT_DATE;
            """)
            count = conn.execute(sql).scalar()
            print(f"Current Count for Parth Today: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_connection_and_data()
