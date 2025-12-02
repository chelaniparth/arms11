from sqlalchemy import create_engine, text
from database import DATABASE_URL

def list_dbs():
    # Connect to the default 'postgres' database to list others
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            print(f"Connected to: {conn.execute(text('SELECT current_database()')).scalar()}")
            
            print("\n--- Available Databases ---")
            result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
            dbs = [row[0] for row in result]
            for db in dbs:
                print(f"- {db}")
                
            print("\n--- Schema Check in 'postgres' DB ---")
            schemas = conn.execute(text("SELECT schema_name FROM information_schema.schemata;"))
            print("Schemas found:", [row[0] for row in schemas])
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_dbs()
