from sqlalchemy.orm import Session
from database import SessionLocal
import models
from sqlalchemy import func

def fix_timestamps():
    db = SessionLocal()
    try:
        print("Fixing missing completed_at timestamps...")
        
        # Find completed tasks with null completed_at
        tasks = db.query(models.Task).filter(
            models.Task.status == models.TaskStatus.Completed,
            models.Task.completed_at == None
        ).all()
        
        count = 0
        for task in tasks:
            print(f"Updating Task {task.task_id}...")
            task.completed_at = func.now()
            task.updated_at = func.now()
            count += 1
            
        db.commit()
        print(f"Successfully updated {count} tasks.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_timestamps()
