import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def fix_trigger():
    print("Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Redefining log_task_changes function...")
        cur.execute("""
        CREATE OR REPLACE FUNCTION arms_workflow.log_task_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Log status changes
            IF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO arms_workflow.task_history (task_id, field_name, old_value, new_value, action)
                VALUES (NEW.task_id, 'status', OLD.status::TEXT, NEW.status::TEXT, 'status_changed');
            END IF;
            
            -- Log assignment changes
            IF OLD.assigned_user_id IS DISTINCT FROM NEW.assigned_user_id THEN
                INSERT INTO arms_workflow.task_history (task_id, field_name, old_value, new_value, action)
                VALUES (NEW.task_id, 'assigned_user_id', OLD.assigned_user_id::TEXT, NEW.assigned_user_id::TEXT, 'assigned');
                
                NEW.assigned_at = NOW();
            END IF;
            
            -- Update tier1_started_at when first moved to In Progress
            IF OLD.status = 'Pending' AND NEW.status = 'In Progress' AND NEW.tier1_started_at IS NULL THEN
                NEW.tier1_started_at = NOW();
            END IF;
            
            -- Update tier1_completed_at when completed
            IF OLD.status != 'Completed' AND NEW.status = 'Completed' AND NEW.tier1_completed_at IS NULL THEN
                NEW.tier1_completed_at = NOW();
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)
        
        conn.commit()
        print("Function redefined successfully.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_trigger()
