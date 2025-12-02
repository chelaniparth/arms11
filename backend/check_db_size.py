from database import SessionLocal, engine
from sqlalchemy import text
from models import Task, User, WorkflowDailyVolume, TaskHistory, TaskComment

def check_size():
    # Get DB Size
    with engine.connect() as conn:
        result = conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database())), pg_database_size(current_database())"))
        pretty_size, size_bytes = result.fetchone()
        
    print(f"Current Database Size: {pretty_size} ({size_bytes} bytes)")
    
    # Get Row Counts
    db = SessionLocal()
    try:
        task_count = db.query(Task).count()
        user_count = db.query(User).count()
        volume_count = db.query(WorkflowDailyVolume).count()
        history_count = db.query(TaskHistory).count()
        comment_count = db.query(TaskComment).count()
        
        print("\nRow Counts:")
        print(f"- Tasks: {task_count}")
        print(f"- Users: {user_count}")
        print(f"- Workflow Volumes: {volume_count}")
        print(f"- Task History: {history_count}")
        print(f"- Comments: {comment_count}")
        
        total_rows = task_count + user_count + volume_count + history_count + comment_count
        if total_rows > 0:
            avg_row_size = size_bytes / total_rows
            print(f"\nApproximate average bytes per record (overhead included): {avg_row_size:.2f} bytes")
            
            # Estimate 500MB
            limit_mb = 500
            limit_bytes = limit_mb * 1024 * 1024
            capacity_rows = limit_bytes / avg_row_size
            print(f"\nEstimation for {limit_mb}MB:")
            print(f"You could store approximately {int(capacity_rows):,} records.")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_size()
