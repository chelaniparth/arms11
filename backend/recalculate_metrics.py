from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from sqlalchemy import func
from datetime import date

def recalculate_metrics():
    db = SessionLocal()
    try:
        today = date.today()
        print(f"Recalculating metrics for {today}...")

        # Get all users
        users = db.query(models.User).all()

        for user in users:
            print(f"Processing user: {user.username}")
            
            # Get tasks for today (created_at or updated_at? Usually performance is based on activity today)
            # For simplicity, let's look at tasks assigned/completed/in-progress currently
            
            # 1. Tasks Assigned Today (or total active assigned?)
            # The UserPerformance model tracks daily stats. 
            # tasks_assigned: Number of tasks assigned to user ON THAT DAY.
            # tasks_completed: Number of tasks completed by user ON THAT DAY.
            
            # Count tasks assigned today
            tasks_assigned_count = db.query(models.Task).filter(
                models.Task.assigned_user_id == user.id,
                func.date(models.Task.assigned_at) == today
            ).count()
            
            # Count tasks completed today
            tasks_completed_count = db.query(models.Task).filter(
                models.Task.assigned_user_id == user.id,
                models.Task.status == models.TaskStatus.Completed,
                func.date(models.Task.completed_at) == today
            ).count()
            
            # Count tasks currently in progress (Snapshot)
            tasks_in_progress_count = db.query(models.Task).filter(
                models.Task.assigned_user_id == user.id,
                models.Task.status == models.TaskStatus.In_Progress
            ).count()

            # Find or create UserPerformance record
            perf = db.query(models.UserPerformance).filter(
                models.UserPerformance.user_id == user.id,
                models.UserPerformance.metric_date == today
            ).first()

            if not perf:
                perf = models.UserPerformance(
                    user_id=user.id,
                    metric_date=today
                )
                db.add(perf)
            
            # Update metrics
            perf.tasks_assigned = tasks_assigned_count
            perf.tasks_completed = tasks_completed_count
            perf.tasks_in_progress = tasks_in_progress_count
            
            print(f"  - Assigned: {tasks_assigned_count}")
            print(f"  - Completed: {tasks_completed_count}")
            print(f"  - In Progress: {tasks_in_progress_count}")

        db.commit()
        print("Metrics recalculation complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recalculate_metrics()
