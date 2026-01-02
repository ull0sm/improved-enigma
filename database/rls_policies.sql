-- EntryDesk Row Level Security Policies
-- Run this AFTER schema.sql in Supabase SQL Editor

-- ============================================
-- HELPER: DROP EXISTING POLICIES (for easy update)
-- ============================================
DROP POLICY IF EXISTS "Anyone can check whitelist" ON allowed_emails;
DROP POLICY IF EXISTS "Admins can insert allowed emails" ON allowed_emails;
DROP POLICY IF EXISTS "Admins can delete allowed emails" ON allowed_emails;

DROP POLICY IF EXISTS "Users can view own profile" ON coaches;
DROP POLICY IF EXISTS "Users can update own profile" ON coaches;
DROP POLICY IF EXISTS "Users can insert own profile" ON coaches;
DROP POLICY IF EXISTS "Admins can view all coaches" ON coaches;

DROP POLICY IF EXISTS "Coaches can view own athletes" ON athletes;
DROP POLICY IF EXISTS "Coaches can insert own athletes" ON athletes;
DROP POLICY IF EXISTS "Coaches can update own athletes" ON athletes;
DROP POLICY IF EXISTS "Coaches can delete own athletes" ON athletes;
DROP POLICY IF EXISTS "Admins can view all athletes" ON athletes;

DROP POLICY IF EXISTS "Authenticated can insert audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Admins can view audit logs" ON audit_logs;

DROP POLICY IF EXISTS "Everyone can read config" ON config;
DROP POLICY IF EXISTS "Admins can update config" ON config;
DROP POLICY IF EXISTS "Admins can insert config" ON config;

DROP POLICY IF EXISTS "Everyone can read dojos" ON dojos;
DROP POLICY IF EXISTS "Authenticated can create dojos" ON dojos;
DROP POLICY IF EXISTS "Admins can update dojos" ON dojos;
DROP POLICY IF EXISTS "Admins can delete dojos" ON dojos;


-- ============================================
-- ENABLE RLS ON ALL TABLES
-- ============================================
ALTER TABLE allowed_emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE coaches ENABLE ROW LEVEL SECURITY;
ALTER TABLE athletes ENABLE ROW LEVEL SECURITY;
ALTER TABLE dojos ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE config ENABLE ROW LEVEL SECURITY;

-- ============================================
-- ALLOWED_EMAILS POLICIES
-- ============================================
-- Anyone can check if an email is in whitelist (for login validation)
CREATE POLICY "Anyone can check whitelist" ON allowed_emails
    FOR SELECT USING (TRUE);

-- Only admins can manage the whitelist
-- FIX: Use allowed_emails check to prevent recursion
CREATE POLICY "Admins can insert allowed emails" ON allowed_emails
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

CREATE POLICY "Admins can delete allowed emails" ON allowed_emails
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

-- ============================================
-- COACHES POLICIES
-- ============================================
-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON coaches
    FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON coaches
    FOR UPDATE USING (auth.uid() = id);

-- Users can insert their own profile (during onboarding)
CREATE POLICY "Users can insert own profile" ON coaches
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Admins can view all coaches
-- FIX: Query allowed_emails directly to break recursion loop with 'coaches' table
CREATE POLICY "Admins can view all coaches" ON coaches
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

-- ============================================
-- ATHLETES POLICIES
-- ============================================
-- Coaches can view their own athletes
CREATE POLICY "Coaches can view own athletes" ON athletes
    FOR SELECT USING (coach_id = auth.uid());

-- Coaches can insert their own athletes
CREATE POLICY "Coaches can insert own athletes" ON athletes
    FOR INSERT WITH CHECK (coach_id = auth.uid());

-- Coaches can update their own athletes
CREATE POLICY "Coaches can update own athletes" ON athletes
    FOR UPDATE USING (coach_id = auth.uid());

-- Coaches can delete their own athletes
CREATE POLICY "Coaches can delete own athletes" ON athletes
    FOR DELETE USING (coach_id = auth.uid());

-- Admins can view ALL athletes (global visibility)
-- FIX: Non-recursive admin check
CREATE POLICY "Admins can view all athletes" ON athletes
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

-- ============================================
-- AUDIT LOGS POLICIES (Append-only, immutable)
-- ============================================
-- Authenticated users can insert audit logs
CREATE POLICY "Authenticated can insert audit logs" ON audit_logs
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Only admins can view audit logs
-- FIX: Non-recursive admin check
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

-- NO UPDATE OR DELETE POLICIES - Audit logs are immutable!

-- ============================================
-- CONFIG POLICIES
-- ============================================
-- Everyone can read config (for tournament name, etc.)
CREATE POLICY "Everyone can read config" ON config
    FOR SELECT USING (TRUE);

-- Only admins can update config
-- FIX: Non-recursive admin check
CREATE POLICY "Admins can update config" ON config
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

CREATE POLICY "Admins can insert config" ON config
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

-- ============================================
-- DOJOS POLICIES
-- ============================================
-- Everyone can read dojos (for dropdowns)
CREATE POLICY "Everyone can read dojos" ON dojos
    FOR SELECT USING (TRUE);

-- Authenticated users can create dojos (during onboarding)
CREATE POLICY "Authenticated can create dojos" ON dojos
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

-- Admins can manage all dojos
-- FIX: Non-recursive admin check
CREATE POLICY "Admins can update dojos" ON dojos
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );

CREATE POLICY "Admins can delete dojos" ON dojos
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM allowed_emails WHERE email = (auth.jwt() ->> 'email') AND is_admin = TRUE)
    );
