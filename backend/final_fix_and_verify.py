from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy import text, func
import models

def fix_and_verify():
    db = SessionLocal()
    try:
        print("--- 1. Fixing NULL Timestamps ---")
        # Fix NULL completed_at
        null_tasks = db.query(models.Task).filter(
            models.Task.status == models.TaskStatus.Completed,
            models.Task.completed_at == None
        ).all()
        
        if null_tasks:
            print(f"Found {len(null_tasks)} tasks with NULL completed_at. Fixing...")
            for t in null_tasks:
                t.completed_at = func.now()
                t.updated_at = func.now()
            db.commit()
            print("Fixed.")
        else:
            print("No NULL timestamps found.")

        print("\n--- 2. Recalculating Metrics ---")
        # (Simplified logic from recalculate_metrics.py)
        today = func.current_date()
        # Reset today's metrics for parth
        user = db.query(models.User).filter(models.User.username == 'parth').first()
        if user:
            perf = db.query(models.UserPerformance).filter(
                models.UserPerformance.user_id == user.id,
                models.UserPerformance.metric_date == today
            ).first()
            
            if not perf:
                perf = models.UserPerformance(user_id=user.id, metric_date=today)
                db.add(perf)
            
            # Count actuals
            completed_count = db.query(models.Task).filter(
                models.Task.assigned_user_id == user.id,
                models.Task.status == models.TaskStatus.Completed,
                func.date(models.Task.completed_at) == today
            ).count()
            
            perf.tasks_completed = completed_count
            db.commit()
            print(f"Metrics updated for parth: {completed_count} completed.")

        print("\n--- 3. Verifying User Query ---")
        # Run the EXACT query the user is trying
        sql = text("""
            SELECT COUNT(*) 
            FROM arms_workflow.tasks t
            JOIN arms_workflow.users u ON t.assigned_user_id = u.id
            WHERE u.username = 'parth'
              AND t.status = 'Completed'
              AND DATE(t.completed_at) = CURRENT_DATE;
        """)
        
        result = db.execute(sql).scalar()
        print(f"SQL Query Result: {result}")
        
        if result == 0:
            print("WARNING: Result is still 0! Checking components...")
            # Debug components
            date_check = db.execute(text("SELECT CURRENT_DATE")).scalar()
            print(f"DB CURRENT_DATE: {date_check}")
            
            count_no_date = db.execute(text("""
                SELECT COUNT(*) 
                FROM arms_workflow.tasks t
                JOIN arms_workflow.users u ON t.assigned_user_id = u.id
                WHERE u.username = 'parth'
                  AND t.status = 'Completed'
            """)).scalar()
            print(f"Count without date filter: {count_no_date}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_and_verify()
