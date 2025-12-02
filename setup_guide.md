# ARMS Workflow System - Setup & Run Guide

This guide explains how to set up the PostgreSQL database and run both the backend and frontend applications.

## 1. Database Setup (PostgreSQL)

The application is already configured to use PostgreSQL. You need to have a PostgreSQL server running.

1.  **Install PostgreSQL**: Download and install from [postgresql.org](https://www.postgresql.org/download/).
2.  **Create Database**:
    Open your terminal or pgAdmin and run the following SQL command to create the database:
    ```sql
    CREATE DATABASE arms_workflow;
    ```
3.  **Configure Connection**:
    Check the `backend/.env` file. It currently points to:
    `postgresql://postgres:1234@127.0.0.1:5432/arms_workflow`
    
    Update the password (`1234`) if your local postgres user has a different password.

## 2. Backend Setup

Open a terminal and navigate to the `backend` directory:
```bash
cd backend
```

### Install Dependencies
If you haven't already, create a virtual environment and install requirements:
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Initialize Database
Run the following command to create all the necessary tables in your PostgreSQL database:
```bash
# This script imports models and creates tables using SQLAlchemy
python -c "from database import engine; import models; models.Base.metadata.create_all(bind=engine)"
```
*Note: The application also attempts to create tables on startup.*

### Start Backend Server
Run the FastAPI server using uvicorn:
```bash
uvicorn main:app --reload --port 8000
```
The backend will be available at `http://localhost:8000`. API docs are at `http://localhost:8000/docs`.

## 3. Frontend Setup

Open a **new** terminal window and navigate to the `frontend` directory:
```bash
cd frontend
```

### Install Dependencies
```bash
npm install
```

### Start Frontend Server
```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`.

## Summary of Commands to Run

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
