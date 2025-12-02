import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def run_schema():
    print(f"Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Reading schema.sql...")
        with open("schema.sql", "r") as f:
            sql = f.read()
            
        print("Executing SQL...")
        cur.execute(sql)
        conn.commit()
        print("Schema executed successfully.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_schema()
