from sqlalchemy.orm import Session
from database import SessionLocal
import models
from sqlalchemy import func
from datetime import date

def debug_data():
    db = SessionLocal()
    try:
        today = date.today()
        print(f"Debug Date: {today}")

        # Find user 'parth'
        user = db.query(models.User).filter(models.User.username == 'parth').first()
        if not user:
            print("User 'parth' not found!")
            return

        print(f"User: {user.username} (ID: {user.id})")

        # Check UserPerformance
        perf = db.query(models.UserPerformance).filter(
            models.UserPerformance.user_id == user.id,
            models.UserPerformance.metric_date == today
        ).first()

        if perf:
            print("\nUserPerformance Record:")
            print(f"  - Date: {perf.metric_date}")
            print(f"  - Assigned: {perf.tasks_assigned}")
            print(f"  - In Progress: {perf.tasks_in_progress}")
            print(f"  - Completed: {perf.tasks_completed}")
        else:
            print("\nNo UserPerformance record found for today.")

        # Check Tasks
        print("\nActual Task Counts (calculated from 'tasks' table):")
        
        assigned_count = db.query(models.Task).filter(
            models.Task.assigned_user_id == user.id,
            func.date(models.Task.assigned_at) == today
        ).count()
        
        completed_count = db.query(models.Task).filter(
            models.Task.assigned_user_id == user.id,
            models.Task.status == models.TaskStatus.Completed
            # Note: We are checking ALL completed tasks for this user, or just today's?
            # Dashboard usually shows "Today's Performance".
            # Let's check both.
        ).count()

        completed_today_count = db.query(models.Task).filter(
            models.Task.assigned_user_id == user.id,
            models.Task.status == models.TaskStatus.Completed,
            func.date(models.Task.completed_at) == today
        ).count()
        
        print(f"  - Assigned Today: {assigned_count}")
        print(f"  - Total Completed (All time): {completed_count}")
        print(f"  - Completed Today: {completed_today_count}")

        # List ALL Completed Tasks
        completed_tasks = db.query(models.Task).filter(
            models.Task.assigned_user_id == user.id,
            models.Task.status == models.TaskStatus.Completed
        ).all()
        
        if completed_tasks:
            print("\nAll Completed Tasks Details:")
            for t in completed_tasks:
                print(f"  - ID: {t.task_id}, Status: {t.status}, Completed At: {t.completed_at}")
        else:
            print("\nNo tasks marked as completed.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    debug_data()
