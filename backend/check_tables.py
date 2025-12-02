from sqlalchemy import create_engine, text
from database import DATABASE_URL

def check_tables():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'arms_workflow'"))
        tables = result.fetchall()
        if tables:
            print(f"Tables found in 'arms_workflow':")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No tables found in 'arms_workflow'.")

if __name__ == "__main__":
    check_tables()
