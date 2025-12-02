from sqlalchemy import create_engine, text
import sys

DATABASE_URL = "postgresql://postgres:1234@127.0.0.1:5432/arms_workflow"

print(f"Testing connection to: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Connection successful!")
        print(f"Result: {result.fetchone()}")
        
        # Check tables
        result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'arms_workflow'"))
        print("\nTables in arms_workflow schema:")
        for row in result:
            print(f"- {row[0]}")
            
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit(1)
