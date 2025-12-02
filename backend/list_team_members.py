from database import SessionLocal
from models import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        print("-" * 20)
        for user in users:
            print(f"- {user.full_name} ({user.username})")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
