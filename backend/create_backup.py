import shutil
import os
import zipfile

def zip_directory(source_dir, output_filename):
    print(f"Zipping {source_dir} to {output_filename}...")
    zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    
    for root, dirs, files in os.walk(source_dir):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git', '.idea', '.vscode', 'dist', 'build', 'coverage']]
        
        for file in files:
            if file == os.path.basename(output_filename):
                continue
            if file.endswith('.pyc') or file.endswith('.pyo') or file.endswith('.pyd') or file.endswith('.DS_Store'):
                continue
                
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, source_dir)
            # print(f"Adding {arcname}")
            zipf.write(file_path, arcname)
            
    zipf.close()
    print(f"Backup created successfully at {output_filename}")

if __name__ == "__main__":
    # Project root is one level up from backend
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) # arms_workflow
    
    # Output to the scratch directory (parent of arms_workflow)
    scratch_dir = os.path.dirname(project_root)
    output_zip = os.path.join(scratch_dir, "arms_workflow_backup.zip")
    
    zip_directory(project_root, output_zip)
