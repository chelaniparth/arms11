from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def debug():
    print(f"DATABASE_URL: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print(f"Connected to {engine.url}")
        try:
            # Check search path
            path = connection.execute(text("SHOW search_path")).scalar()
            print(f"Search path: {path}")

            # Check if schema exists
            schema = connection.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'arms_workflow'")).scalar()
            print(f"Schema 'arms_workflow' exists: {schema}")

            # Check if table exists
            table = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'arms_workflow' AND table_name = 'users'")).scalar()
            print(f"Table 'arms_workflow.users' exists: {table}")

            # Try query
            result = connection.execute(text("SELECT count(*) FROM arms_workflow.users"))
            print(f"Count: {result.scalar()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug()
