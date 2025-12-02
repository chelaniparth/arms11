from sqlalchemy import create_engine, text
import os

# Base URL structure
BASE_URL = "postgresql://postgres:1234@127.0.0.1:5432"

def check_db(db_name):
    url = f"{BASE_URL}/{db_name}"
    print(f"\n--- Checking Database: '{db_name}' ---")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            # Check if schema exists
            schema_exists = conn.execute(text("SELECT 1 FROM information_schema.schemata WHERE schema_name = 'arms_workflow'")).scalar()
            if not schema_exists:
                print(f"  [X] Schema 'arms_workflow' DOES NOT EXIST.")
                return

            print(f"  [OK] Schema 'arms_workflow' exists.")
            
            # Check table exists
            table_exists = conn.execute(text("SELECT 1 FROM information_schema.tables WHERE table_schema = 'arms_workflow' AND table_name = 'tasks'")).scalar()
            if not table_exists:
                print(f"  [X] Table 'arms_workflow.tasks' DOES NOT EXIST.")
                return

            # Count tasks
            count = conn.execute(text("SELECT COUNT(*) FROM arms_workflow.tasks")).scalar()
            print(f"  [!] Total Tasks Found: {count}")
            
            # Count completed for parth
            try:
                sql = text("""
                    SELECT COUNT(*) 
                    FROM arms_workflow.tasks t
                    JOIN arms_workflow.users u ON t.assigned_user_id = u.id
                    WHERE u.username = 'parth' AND t.status = 'Completed'
                """)
                parth_count = conn.execute(sql).scalar()
                print(f"  [!] Completed Tasks for Parth: {parth_count}")
            except Exception as e:
                print(f"  [X] Could not query parth's tasks: {e}")

    except Exception as e:
        print(f"  [X] Connection Failed: {e}")

if __name__ == "__main__":
    check_db("postgres")
    check_db("arms_workflow")
