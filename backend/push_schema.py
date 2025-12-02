from database import engine, Base
import models

def push_schema():
    print("Pushing schema to database...")
    # This will create tables if they don't exist.
    # It will NOT update existing tables (e.g. adding columns).
    Base.metadata.create_all(bind=engine)
    print("Schema push complete.")

if __name__ == "__main__":
    push_schema()
