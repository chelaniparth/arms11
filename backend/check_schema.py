from database import engine
from sqlalchemy import text

def check_schema():
    with engine.connect() as conn:
        # Check tables
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'arms_workflow'"))
        tables = [row[0] for row in result]
        print("Tables in arms_workflow:", tables)

        # Check trigger function definition
        result = conn.execute(text("SELECT prosrc FROM pg_proc WHERE proname = 'log_task_changes'"))
        function_def = result.scalar()
        print("\nFunction log_task_changes definition:")
        print(function_def)

if __name__ == "__main__":
    check_schema()
