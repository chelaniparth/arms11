-- ============================================
-- ARMS Workflow Management Database Schema
-- PostgreSQL / Supabase Compatible
-- ============================================

-- Create custom schema
CREATE SCHEMA IF NOT EXISTS arms_workflow;
SET search_path TO arms_workflow, public;

-- ============================================
-- ENUMS for type safety
-- ============================================

DO $$ BEGIN
    CREATE TYPE task_status AS ENUM (
        'Pending',
        'In Progress',
        'Completed',
        'Under Review',
        'Paused'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_priority AS ENUM (
        'Low',
        'Medium',
        'High',
        'Critical'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE task_type AS ENUM (
        'Tier I',
        'Tier II'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'admin',
        'manager',
        'analyst'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE workflow_type AS ENUM (
        'Pending',
        'UCC',
        'Judgements',
        'Chapter11',
        'Chapter7',
        'Trade Tapes',
        'Volume',
        'Target'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE notification_type AS ENUM (
        'info',
        'success',
        'warning',
        'error'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- CORE TABLES
-- ============================================

-- Users table (extends Supabase auth.users if available, otherwise standalone)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'analyst',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    
    -- Supabase auth integration (nullable for local dev)
    auth_user_id UUID
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    task_id SERIAL PRIMARY KEY,
    task_type task_type NOT NULL,
    company_name VARCHAR(500) NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    priority task_priority NOT NULL DEFAULT 'Medium',
    status task_status NOT NULL DEFAULT 'Pending',
    
    -- Assignment
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE,
    
    -- Dates and tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tier1_started_at TIMESTAMP WITH TIME ZONE,
    tier1_completed_at TIMESTAMP WITH TIME ZONE,
    tier2_started_at TIMESTAMP WITH TIME ZONE,
    tier2_completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    description TEXT,
    notes TEXT,
    source VARCHAR(100), -- 'manual', 'email', 'api', 'bulk_upload'
    email_reference VARCHAR(255),
    
    -- SLA tracking
    sla_hours INTEGER DEFAULT 72,
    sla_hours INTEGER DEFAULT 72,
    due_date TIMESTAMP WITH TIME ZONE,
    
    -- New columns for production tracking
    target_qty INTEGER DEFAULT 1,
    achieved_qty INTEGER DEFAULT 0,
    rating INTEGER,
    remarks TEXT,
    picked_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT valid_dates CHECK (
        tier1_completed_at IS NULL OR tier1_completed_at >= tier1_started_at
    )
);

-- Task files/attachments
CREATE TABLE IF NOT EXISTS task_attachments (
    attachment_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    file_name VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size_bytes BIGINT,
    storage_path TEXT NOT NULL, -- Supabase storage path
    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- File metadata
    is_output BOOLEAN DEFAULT FALSE, -- TRUE for completed work files
    file_category VARCHAR(50) -- '10-Q', '10-K', 'email', 'output'
);

-- Task history/audit log
CREATE TABLE IF NOT EXISTS task_history (
    history_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    changed_by UUID REFERENCES users(id),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Change tracking
    field_name VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    action VARCHAR(50), -- 'created', 'updated', 'assigned', 'status_changed'
    
    -- Additional context
    notes TEXT
);

-- Comments/notes on tasks
CREATE TABLE IF NOT EXISTS task_comments (
    comment_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_internal BOOLEAN DEFAULT FALSE -- for manager-only notes
);

-- Workflow configurations
CREATE TABLE IF NOT EXISTS workflow_configs (
    config_id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(255) NOT NULL UNIQUE,
    workflow_type workflow_type NOT NULL,
    
    -- Metrics
    target_metric VARCHAR(100),
    measurement_unit VARCHAR(100),
    monthly_target VARCHAR(100),
    
    -- Settings
    priority task_priority DEFAULT 'Medium',
    sla_hours INTEGER DEFAULT 72,
    quality_required BOOLEAN DEFAULT TRUE,
    
    -- Data points (JSON array of required fields)
    data_points JSONB,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- Email triggers for task creation
CREATE TABLE IF NOT EXISTS email_triggers (
    trigger_id SERIAL PRIMARY KEY,
    email_address VARCHAR(255) NOT NULL,
    subject_pattern VARCHAR(500), -- Regex pattern to match
    sender_whitelist TEXT[], -- Array of allowed sender emails
    
    -- Auto-task creation settings
    auto_create_task BOOLEAN DEFAULT TRUE,
    default_task_type task_type,
    default_priority task_priority,
    workflow_config_id INTEGER REFERENCES workflow_configs(config_id),
    
    -- Assignment rules
    auto_assign BOOLEAN DEFAULT FALSE,
    assign_to_user_id UUID REFERENCES users(id),
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Processed emails log
CREATE TABLE IF NOT EXISTS processed_emails (
    email_id SERIAL PRIMARY KEY,
    trigger_id INTEGER REFERENCES email_triggers(trigger_id),
    
    -- Email details
    email_subject VARCHAR(500),
    email_from VARCHAR(255),
    email_date TIMESTAMP WITH TIME ZONE,
    email_body TEXT,
    
    -- Processing
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    task_created_id INTEGER REFERENCES tasks(task_id),
    processing_status VARCHAR(50), -- 'success', 'failed', 'duplicate'
    error_message TEXT
);

-- Analytics/metrics snapshots (for dashboard)
CREATE TABLE IF NOT EXISTS daily_metrics (
    metric_id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    
    -- Task metrics
    total_tasks INTEGER DEFAULT 0,
    pending_tasks INTEGER DEFAULT 0,
    in_progress_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    under_review_tasks INTEGER DEFAULT 0,
    
    -- Performance metrics
    avg_completion_time_hours NUMERIC(10, 2),
    tasks_completed_on_time INTEGER DEFAULT 0,
    tasks_completed_late INTEGER DEFAULT 0,
    
    -- User metrics (JSON for per-analyst breakdown)
    user_metrics JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_metric_date UNIQUE(metric_date)
);

-- User performance tracking
CREATE TABLE IF NOT EXISTS user_performance (
    performance_id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    metric_date DATE NOT NULL,
    
    -- Daily metrics
    tasks_assigned INTEGER DEFAULT 0,
    tasks_completed INTEGER DEFAULT 0,
    tasks_in_progress INTEGER DEFAULT 0,
    avg_completion_time_hours NUMERIC(10, 2),
    
    -- Quality metrics
    tasks_under_review INTEGER DEFAULT 0,
    tasks_rejected INTEGER DEFAULT 0,
    quality_score NUMERIC(5, 2), -- 0-100 scale
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_user_metric_date UNIQUE(user_id, metric_date)
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type notification_type DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INDEXES for Performance
-- ============================================

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_user ON tasks(assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_company ON tasks(company_name);
CREATE INDEX IF NOT EXISTS idx_task_history_task_id ON task_history(task_id);
CREATE INDEX IF NOT EXISTS idx_task_attachments_task_id ON task_attachments(task_id);
CREATE INDEX IF NOT EXISTS idx_user_performance_user_date ON user_performance(user_id, metric_date);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to relevant tables
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_workflow_configs_updated_at ON workflow_configs;
CREATE TRIGGER update_workflow_configs_updated_at BEFORE UPDATE ON workflow_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to log task changes
CREATE OR REPLACE FUNCTION log_task_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Log status changes
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO arms_workflow.task_history (task_id, field_name, old_value, new_value, action)
        VALUES (NEW.task_id, 'status', OLD.status::TEXT, NEW.status::TEXT, 'status_changed');
    END IF;
    
    -- Log assignment changes
    IF OLD.assigned_user_id IS DISTINCT FROM NEW.assigned_user_id THEN
        INSERT INTO arms_workflow.task_history (task_id, field_name, old_value, new_value, action)
        VALUES (NEW.task_id, 'assigned_user_id', OLD.assigned_user_id::TEXT, NEW.assigned_user_id::TEXT, 'assigned');
        
        NEW.assigned_at = NOW();
    END IF;
    
    -- Update tier1_started_at when first moved to In Progress
    IF OLD.status = 'Pending' AND NEW.status = 'In Progress' AND NEW.tier1_started_at IS NULL THEN
        NEW.tier1_started_at = NOW();
    END IF;
    
    -- Update tier1_completed_at when completed
    IF OLD.status != 'Completed' AND NEW.status = 'Completed' AND NEW.tier1_completed_at IS NULL THEN
        NEW.tier1_completed_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS task_changes_trigger ON tasks;
CREATE TRIGGER task_changes_trigger BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION log_task_changes();

-- Function to calculate and update daily metrics
CREATE OR REPLACE FUNCTION calculate_daily_metrics(target_date DATE DEFAULT CURRENT_DATE)
RETURNS VOID AS $$
BEGIN
    INSERT INTO daily_metrics (
        metric_date,
        total_tasks,
        pending_tasks,
        in_progress_tasks,
        completed_tasks,
        under_review_tasks,
        avg_completion_time_hours,
        tasks_completed_on_time,
        tasks_completed_late
    )
    SELECT
        target_date,
        COUNT(*),
        COUNT(*) FILTER (WHERE status = 'Pending'),
        COUNT(*) FILTER (WHERE status = 'In Progress'),
        COUNT(*) FILTER (WHERE status = 'Completed'),
        COUNT(*) FILTER (WHERE status = 'Under Review'),
        AVG(EXTRACT(EPOCH FROM (tier1_completed_at - tier1_started_at)) / 3600) 
            FILTER (WHERE tier1_completed_at IS NOT NULL),
        COUNT(*) FILTER (WHERE status = 'Completed' AND tier1_completed_at <= due_date),
        COUNT(*) FILTER (WHERE status = 'Completed' AND tier1_completed_at > due_date)
    FROM tasks
    WHERE DATE(created_at) <= target_date
    ON CONFLICT (metric_date) DO UPDATE SET
        total_tasks = EXCLUDED.total_tasks,
        pending_tasks = EXCLUDED.pending_tasks,
        in_progress_tasks = EXCLUDED.in_progress_tasks,
        completed_tasks = EXCLUDED.completed_tasks,
        under_review_tasks = EXCLUDED.under_review_tasks,
        avg_completion_time_hours = EXCLUDED.avg_completion_time_hours,
        tasks_completed_on_time = EXCLUDED.tasks_completed_on_time,
        tasks_completed_late = EXCLUDED.tasks_completed_late;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- ROW LEVEL SECURITY (RLS) for Supabase
-- ============================================

-- Enable RLS on tables
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE task_attachments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE task_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE task_comments ENABLE ROW LEVEL SECURITY;

-- Users can read their own data
-- DROP POLICY IF EXISTS "Users can view own data" ON users;
-- CREATE POLICY "Users can view own data" ON users
--     FOR SELECT USING (auth_user_id IS NULL OR auth_user_id = auth.uid()); -- Modified for local dev compatibility

-- Managers can view all users
-- DROP POLICY IF EXISTS "Managers can view all users" ON users;
-- CREATE POLICY "Managers can view all users" ON users
--     FOR SELECT USING (
--         EXISTS (
--             SELECT 1 FROM users 
--             WHERE (auth_user_id = auth.uid() OR auth_user_id IS NULL)
--             AND role = 'manager'
--         )
--     );

-- Analysts can view their assigned tasks
-- DROP POLICY IF EXISTS "Analysts can view assigned tasks" ON tasks;
-- CREATE POLICY "Analysts can view assigned tasks" ON tasks
--     FOR SELECT USING (
--         assigned_user_id IN (
--             SELECT id FROM users WHERE (auth_user_id = auth.uid() OR auth_user_id IS NULL)
--         )
--         OR
--         EXISTS (
--             SELECT 1 FROM users 
--             WHERE (auth_user_id = auth.uid() OR auth_user_id IS NULL)
--             AND role IN ('manager', 'admin')
--         )
--     );

-- Analysts can update their assigned tasks
-- DROP POLICY IF EXISTS "Analysts can update assigned tasks" ON tasks;
-- CREATE POLICY "Analysts can update assigned tasks" ON tasks
--     FOR UPDATE USING (
--         assigned_user_id IN (
--             SELECT id FROM users WHERE (auth_user_id = auth.uid() OR auth_user_id IS NULL)
--         )
--         OR
--         EXISTS (
--             SELECT 1 FROM users 
--             WHERE (auth_user_id = auth.uid() OR auth_user_id IS NULL)
--             AND role IN ('manager', 'admin')
--         )
--     );

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert sample users (passwords will be managed by Supabase Auth)
-- INSERT INTO users (username, email, full_name, role) VALUES
-- ('admin', 'admin@arms.com', 'System Administrator', 'admin'),
-- ('nisarg', 'nisarg@arms.com', 'Nisarg Thakker', 'analyst'),
-- ('komal', 'komal@arms.com', 'Komal Khamar', 'analyst'),
-- ('ayushi', 'ayushi@arms.com', 'Ayushi Chandel', 'analyst'),
-- ('jen', 'jen@arms.com', 'Jen Shears', 'analyst'),
-- ('rondrea', 'rondrea@arms.com', 'Rondrea Carroll', 'analyst'),
-- ('devanshi', 'devanshi@arms.com', 'Devanshi Joshi', 'analyst'),
-- ('divyesh', 'divyesh@arms.com', 'Divyesh Fofandi', 'analyst'),
-- ('parth', 'parth@arms.com', 'Parth Chelani', 'analyst'),
-- ('prerna', 'prerna@arms.com', 'Prerna Kesrani', 'analyst'),
-- ('ankit', 'ankit@arms.com', 'Ankit Rawat', 'analyst')
-- ON CONFLICT (username) DO NOTHING;

-- Insert sample workflow configurations
INSERT INTO workflow_configs (
    workflow_name, workflow_type, target_metric, measurement_unit, 
    monthly_target, priority, sla_hours, quality_required
) VALUES
('Trades Tape Imports', 'Trade Tapes', 'Completion %', 'Batches', '100%', 'High', 24, TRUE),
('Pending Items', 'Pending', 'Completion %', 'Items', '100%', 'High', 72, TRUE),
('Placements', 'Target', 'Placements', 'Cases', '50', 'Medium', 72, TRUE),
('Judgments', 'Judgements', 'Accuracy %', 'Judgments', '98%', 'Medium', 72, TRUE),
('UCC Filings', 'UCC', 'UCC Filings', 'Filings', '30', 'Medium', 72, TRUE)
ON CONFLICT (workflow_name) DO NOTHING;

-- ============================================
-- VIEWS for Easy Querying
-- ============================================

-- View for task overview with user names
CREATE OR REPLACE VIEW v_task_overview AS
SELECT 
    t.task_id,
    t.task_type,
    t.company_name,
    t.document_type,
    t.priority,
    t.status,
    u.full_name AS assigned_user_name,
    u.username AS assigned_username,
    t.created_at,
    t.tier1_completed_at,
    t.due_date,
    CASE 
        WHEN t.due_date IS NOT NULL AND t.tier1_completed_at IS NULL 
        THEN EXTRACT(EPOCH FROM (t.due_date - NOW())) / 3600
        ELSE NULL 
    END AS hours_until_due,
    CASE 
        WHEN t.tier1_completed_at IS NOT NULL AND t.tier1_started_at IS NOT NULL
        THEN EXTRACT(EPOCH FROM (t.tier1_completed_at - t.tier1_started_at)) / 3600
        ELSE NULL
    END AS completion_time_hours
FROM tasks t
LEFT JOIN users u ON t.assigned_user_id = u.id;

-- View for analyst performance summary
CREATE OR REPLACE VIEW v_analyst_performance AS
SELECT 
    u.id AS user_id,
    u.full_name,
    u.username,
    COUNT(t.task_id) AS total_tasks,
    COUNT(t.task_id) FILTER (WHERE t.status = 'Completed') AS completed_tasks,
    COUNT(t.task_id) FILTER (WHERE t.status = 'In Progress') AS in_progress_tasks,
    COUNT(t.task_id) FILTER (WHERE t.status = 'Pending') AS pending_tasks,
    ROUND(
        COUNT(t.task_id) FILTER (WHERE t.status = 'Completed')::NUMERIC / 
        NULLIF(COUNT(t.task_id), 0) * 100, 
        1
    ) AS completion_rate_percent,
    AVG(
        EXTRACT(EPOCH FROM (t.tier1_completed_at - t.tier1_started_at)) / 3600
    ) FILTER (WHERE t.tier1_completed_at IS NOT NULL) AS avg_completion_hours
FROM users u
LEFT JOIN tasks t ON u.id = t.assigned_user_id
WHERE u.role = 'analyst'
GROUP BY u.id, u.full_name, u.username;

-- Grant necessary permissions
-- GRANT USAGE ON SCHEMA arms_workflow TO authenticated, anon;
-- GRANT ALL ON ALL TABLES IN SCHEMA arms_workflow TO authenticated;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA arms_workflow TO authenticated;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA arms_workflow TO authenticated;

-- Refresh views permissions
-- GRANT SELECT ON v_task_overview TO authenticated, anon;
-- GRANT SELECT ON v_analyst_performance TO authenticated, anon;
