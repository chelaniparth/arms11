from sqlalchemy.orm import Session
from database import SessionLocal
import models
from sqlalchemy import text

def investigate():
    db = SessionLocal()
    try:
        print("--- Database Time Check ---")
        result = db.execute(text("SELECT CURRENT_DATE, NOW(), current_setting('TIMEZONE');")).fetchone()
        print(f"DB Current Date: {result[0]}")
        print(f"DB Now: {result[1]}")
        print(f"DB Timezone: {result[2]}")
        
        print("\n--- Parth's Completed Tasks ---")
        # Find user 'parth'
        user = db.query(models.User).filter(models.User.username == 'parth').first()
        if not user:
            print("User 'parth' not found!")
            return

        tasks = db.query(models.Task).filter(
            models.Task.assigned_user_id == user.id,
            models.Task.status == models.TaskStatus.Completed
        ).all()
        
        print(f"Found {len(tasks)} completed tasks for parth.")
        for t in tasks:
            print(f"ID: {t.task_id} | Status: {t.status} | Completed At: {t.completed_at} | Updated At: {t.updated_at}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    investigate()
