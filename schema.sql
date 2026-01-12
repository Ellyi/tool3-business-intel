-- Business Intelligence Auditor Database Schema
-- Run this on Railway PostgreSQL after deployment

-- Main audit records
CREATE TABLE IF NOT EXISTS audits (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    team_size VARCHAR(50),
    responses JSONB NOT NULL,
    intelligence_score INTEGER NOT NULL,
    opportunities JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Detailed waste zone results
CREATE TABLE IF NOT EXISTS audit_results (
    id SERIAL PRIMARY KEY,
    audit_id INTEGER REFERENCES audits(id) ON DELETE CASCADE,
    waste_zone VARCHAR(255) NOT NULL,
    waste_score INTEGER NOT NULL,
    time_wasted_monthly INTEGER,
    automation_complexity VARCHAR(50),
    estimated_roi INTEGER,
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- CIP: Pattern learning
CREATE TABLE IF NOT EXISTS audit_patterns (
    id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(100) NOT NULL,
    pattern_data JSONB NOT NULL,
    frequency INTEGER DEFAULT 1,
    avg_score DECIMAL(5,2),
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(pattern_type, pattern_data)
);

-- CIP: Generated insights
CREATE TABLE IF NOT EXISTS intelligence_insights (
    id SERIAL PRIMARY KEY,
    insight_type VARCHAR(50),
    insight_text TEXT NOT NULL,
    confidence DECIMAL(3,2),
    supporting_data JSONB,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audits_created ON audits(created_at);
CREATE INDEX IF NOT EXISTS idx_audits_industry ON audits(industry);
CREATE INDEX IF NOT EXISTS idx_audits_score ON audits(intelligence_score);
CREATE INDEX IF NOT EXISTS idx_results_audit ON audit_results(audit_id);
CREATE INDEX IF NOT EXISTS idx_results_zone ON audit_results(waste_zone);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON audit_patterns(pattern_type);
```

