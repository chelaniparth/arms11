from sqlalchemy import create_engine, text
from database import DATABASE_URL

def check_schema():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'arms_workflow'"))
        schema = result.fetchone()
        if schema:
            print(f"Schema found: {schema[0]}")
        else:
            print("Schema 'arms_workflow' NOT found.")

if __name__ == "__main__":
    check_schema()
