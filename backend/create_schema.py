from sqlalchemy import create_engine, text
from database import DATABASE_URL

def create_schema():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS arms_workflow"))
        connection.commit()
        print("Schema 'arms_workflow' created successfully.")

if __name__ == "__main__":
    create_schema()
