from sqlalchemy import create_engine, text
from database import DATABASE_URL

def check_enum():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT enum_range(NULL::arms_workflow.workflow_type)")).scalar()
        print(f"Existing Enum Values: {result}")

if __name__ == "__main__":
    check_enum()
