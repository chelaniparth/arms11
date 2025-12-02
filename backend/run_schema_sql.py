from sqlalchemy import create_engine, text
from database import DATABASE_URL
import os

def run_schema():
    print(f"Connecting to {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    schema_file = "schema.sql"
    if not os.path.exists(schema_file):
        print(f"Error: {schema_file} not found.")
        return

    with open(schema_file, "r") as f:
        sql_content = f.read()

    # Split by semicolon is risky with functions, but let's try executing the whole block
    # Psycopg2 usually handles multiple statements in one execute call
    
    try:
        with engine.connect() as connection:
            # We need to use execution_options(isolation_level="AUTOCOMMIT") for some statements like CREATE DATABASE (not here)
            # But for CREATE SCHEMA and types, standard transaction should be fine.
            # However, mixing some statements might require autocommit.
            
            # Let's try executing the whole file
            connection.execute(text(sql_content))
            connection.commit()
            print("Schema executed successfully.")
    except Exception as e:
        print(f"Error executing schema: {e}")

if __name__ == "__main__":
    run_schema()
