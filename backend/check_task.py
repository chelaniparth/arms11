from database import SessionLocal
import models
from sqlalchemy import desc

def check_last_task():
    db = SessionLocal()
    try:
        task = db.query(models.Task).order_by(desc(models.Task.created_at)).first()
        if task:
            print(f"Task ID: {task.task_id}")
            print(f"Company Name: {task.company_name}")
            print(f"Target Qty: {task.target_qty}")
            print(f"Status: {task.status}")
        else:
            print("No tasks found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_last_task()
