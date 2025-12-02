from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path
from security import get_password_hash

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/arms_workflow")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_db():
    db = SessionLocal()
    try:
        # Add password_hash column if it doesn't exist
        print("Checking for password_hash column...")
        try:
            db.execute(text("ALTER TABLE arms_workflow.users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)"))
            db.commit()
            print("Column added or already exists.")
        except Exception as e:
            print(f"Error adding column: {e}")
            db.rollback()

        # Update admin password
        print("Updating admin password...")
        hashed_pwd = get_password_hash("admin123")
        db.execute(text("UPDATE arms_workflow.users SET password_hash = :pwd WHERE username = 'admin'"), {"pwd": hashed_pwd})
        
        # Update other users for testing
        default_pwd = get_password_hash("password")
        db.execute(text("UPDATE arms_workflow.users SET password_hash = :pwd WHERE username != 'admin' AND password_hash IS NULL"), {"pwd": default_pwd})
        
        db.commit()
        print("Passwords updated.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_db()
