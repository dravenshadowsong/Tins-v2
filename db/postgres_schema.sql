-- PostgreSQL Schema for TINS Talent Management System

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS centers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'facilitator',
    active INTEGER DEFAULT 1,
    center_id INTEGER REFERENCES centers(id) ON DELETE SET NULL,
    student_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS children (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    language VARCHAR(50) NOT NULL DEFAULT 'Hindi',
    school_year VARCHAR(50),
    gender VARCHAR(50),
    exp_kinesthetic INTEGER DEFAULT 0,
    exp_creative INTEGER DEFAULT 0,
    exp_logical INTEGER DEFAULT 0,
    exp_spatial INTEGER DEFAULT 0,
    exp_social INTEGER DEFAULT 0,
    exp_language INTEGER DEFAULT 0,
    exp_naturalist INTEGER DEFAULT 0,
    exp_intrapersonal INTEGER DEFAULT 0,
    center_id INTEGER REFERENCES centers(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    phase VARCHAR(50) NOT NULL DEFAULT 'discovery',
    responses TEXT,
    domain_flags TEXT,
    tq_scores TEXT,
    eq_score INTEGER,
    visualizer_score INTEGER,
    personality_data TEXT,
    integrated_score TEXT,
    top_domain VARCHAR(100),
    generated_tasks TEXT,
    status VARCHAR(50) DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facilitator_notes (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    facilitator VARCHAR(255),
    confirmed INTEGER DEFAULT 0,
    observation TEXT,
    override_domain VARCHAR(100),
    notes TEXT,
    agreement VARCHAR(50) DEFAULT 'Agree',
    strengths_observed TEXT,
    concerns TEXT,
    suggested_workshop VARCHAR(255),
    obs_creativity INTEGER DEFAULT 0,
    obs_communication INTEGER DEFAULT 0,
    obs_leadership INTEGER DEFAULT 0,
    obs_focus INTEGER DEFAULT 0,
    obs_curiosity INTEGER DEFAULT 0,
    evidence_notes TEXT,
    validation_status VARCHAR(100) DEFAULT 'Pending Validation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mentors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    bio TEXT,
    contact VARCHAR(255),
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS mentor_matches (
    id SERIAL PRIMARY KEY,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    mentor_id INTEGER NOT NULL REFERENCES mentors(id) ON DELETE CASCADE,
    domain VARCHAR(100),
    plan TEXT,
    status VARCHAR(50) DEFAULT 'active',
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS milestones (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES mentor_matches(id) ON DELETE CASCADE,
    title VARCHAR(255),
    due_date VARCHAR(50),
    done INTEGER DEFAULT 0,
    note TEXT
);

CREATE TABLE IF NOT EXISTS workshops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    center_id INTEGER REFERENCES centers(id) ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workshop_sessions (
    id SERIAL PRIMARY KEY,
    workshop_id INTEGER NOT NULL REFERENCES workshops(id) ON DELETE CASCADE,
    session_date VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workshop_attendance (
    id SERIAL PRIMARY KEY,
    workshop_session_id INTEGER NOT NULL REFERENCES workshop_sessions(id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- 'Present' or 'Absent'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mentor_validations (
    id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL REFERENCES mentor_matches(id) ON DELETE CASCADE,
    child_id INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    domain VARCHAR(100) NOT NULL,
    rating INTEGER DEFAULT 3,
    strengths TEXT,
    growth_areas TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS puzzles (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) NOT NULL,
    domain VARCHAR(50) NOT NULL,
    component VARCHAR(100),
    data TEXT, -- JSON structure of the puzzle prompt/options
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
