-- EntryDesk Database Schema
-- Run this in Supabase SQL Editor

-- ============================================
-- 1. ALLOWED EMAILS (Whitelist - Admin controlled)
-- ============================================
CREATE TABLE IF NOT EXISTS allowed_emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    is_admin BOOLEAN DEFAULT FALSE,
    added_by UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. DOJOS/CLUBS
-- ============================================
CREATE TABLE IF NOT EXISTS dojos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. COACHES (Linked to Supabase Auth)
-- ============================================
CREATE TABLE IF NOT EXISTS coaches (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    phone TEXT,
    dojo_id UUID REFERENCES dojos(id),
    is_admin BOOLEAN DEFAULT FALSE,
    onboarding_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 4. ATHLETES
-- ============================================
CREATE TABLE IF NOT EXISTS athletes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coach_id UUID NOT NULL REFERENCES coaches(id) ON DELETE CASCADE,
    dojo_id UUID NOT NULL REFERENCES dojos(id),
    full_name TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female')),
    belt_rank TEXT NOT NULL,
    weight_kg NUMERIC(5,2),
    competition_day TEXT NOT NULL CHECK (competition_day IN ('Day 1', 'Day 2', 'Both')),
    kata_event BOOLEAN DEFAULT FALSE,
    kumite_event BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint for duplicate prevention (Name + DOB + Dojo)
    UNIQUE(full_name, date_of_birth, dojo_id)
);

-- ============================================
-- 5. AUDIT LOGS (Immutable - The "Black Box")
-- ============================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action TEXT NOT NULL CHECK (action IN ('REGISTER', 'UPDATE', 'DELETE', 'BULK_REGISTER')),
    athlete_data JSONB NOT NULL,
    coach_id UUID NOT NULL,
    coach_email TEXT NOT NULL,
    dojo_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 6. CONFIGURATION (Admin-managed settings)
-- ============================================
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES coaches(id)
);

-- ============================================
-- DEFAULT DATA
-- ============================================

-- Default configuration values
INSERT INTO config (key, value) VALUES 
    ('tournament_name', '"National Karate Championship 2026"'),
    ('registration_open', 'true'),
    ('registration_deadline', '"2026-02-15T23:59:59Z"'),
    ('tournament_dates', '{"day1": "2026-03-01", "day2": "2026-03-02"}')
ON CONFLICT (key) DO NOTHING;

-- ============================================
-- IMPORTANT: Insert your first admin email here!
-- Change 'admin@example.com' to your actual email
-- ============================================
INSERT INTO allowed_emails (email, is_admin) VALUES 
    ('admin@example.com', TRUE)
ON CONFLICT (email) DO NOTHING;

-- ============================================
-- INDEXES for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_athletes_coach_id ON athletes(coach_id);
CREATE INDEX IF NOT EXISTS idx_athletes_dojo_id ON athletes(dojo_id);
CREATE INDEX IF NOT EXISTS idx_athletes_name_dob ON athletes(full_name, date_of_birth);
CREATE INDEX IF NOT EXISTS idx_coaches_email ON coaches(email);
CREATE INDEX IF NOT EXISTS idx_allowed_emails_email ON allowed_emails(email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_coach_id ON audit_logs(coach_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);
