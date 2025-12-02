from database import engine
import models
from sqlalchemy import text

def create_tables():
    # Ensure schema exists
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS arms_workflow"))
        connection.execute(text("SET search_path TO arms_workflow, public"))
        connection.commit()
        print("Schema 'arms_workflow' checked/created and search_path set.")

    print("Creating tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
