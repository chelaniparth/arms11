from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL
import models
from datetime import datetime

def verify_task_creation():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Attempting to create a task...")
        new_task = models.Task(
            task_type="Tier I",
            company_name="Test Company",
            document_type="10-K",
            priority="Medium",
            status="Pending",
            description="Test task description",
            target_qty=5,
            achieved_qty=0
        )
        db.add(new_task)
        db.commit()
        print(f"Task created successfully. ID: {new_task.task_id}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_task_creation()
