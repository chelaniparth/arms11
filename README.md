# ARMS Workflow System

## Quick Start Guide

### 1. Start the Application
To start both the Backend and Frontend servers, simply double-click the `start_app.bat` file in this directory.

Or run it from the command line:
```cmd
start_app.bat
```

This will:
- Stop any running Python/Node processes.
- Start the Backend API on http://localhost:8000
- Start the Frontend UI on http://localhost:5173

### 2. Setup/Reset Database
If you need to push all schema changes to the database (or if setting up for the first time), run the setup script:

```cmd
python setup_database.py
```

This script will:
- Create all database tables.
- Update Enum types (Task Types, Roles, etc.).
- Create the Admin user (`admin` / `admin`).
- Create the 'Parth' user.
- Seed initial data.

## Manual Startup (If needed)

**Backend:**
```cmd
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Frontend:**
```cmd
cd frontend
npm run dev
```

## Default Logins
- **Admin**: `admin` / `admin`
- **Parth**: `parth` / `admin`
