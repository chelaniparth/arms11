from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import DATABASE_URL
import models

def verify_access():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Attempting to query arms_workflow.notifications...")
        # Try raw SQL first
        result = db.execute(text("SELECT count(*) FROM arms_workflow.notifications"))
        print(f"Raw SQL Count: {result.scalar()}")
        
        # Try ORM
        print("Attempting ORM query...")
        count = db.query(models.Notification).count()
        print(f"ORM Count: {count}")
        
        print("Access successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_access()
