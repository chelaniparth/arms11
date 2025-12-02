import subprocess
import os
import sys

def run_script(script_name):
    print(f"Running {script_name}...")
    try:
        # Use the current python executable
        result = subprocess.run([sys.executable, script_name], check=True, capture_output=True, text=True)
        print(f"Success: {script_name}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stderr)
        # We don't exit here because some scripts might fail if things already exist (which is fine)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, 'backend')
    
    scripts = [
        # 1. Base Schema
        'run_schema_sql.py',
        
        # 2. Fixes and Updates
        'update_enum_types.py',
        'create_missing_notifications_table.py',
        'add_password_column.py',
        
        # 3. User Seeding
        'create_admin_user.py',
        'manage_parth_user.py',
        'seed_users.py' 
    ]
    
    print("Starting Database Setup...")
    print("--------------------------------")
    
    for script in scripts:
        script_path = os.path.join(backend_dir, script)
        if os.path.exists(script_path):
            run_script(script_path)
        else:
            print(f"Warning: Script not found: {script_path}")
            
    print("--------------------------------")
    print("Database Setup Completed.")

if __name__ == "__main__":
    main()
