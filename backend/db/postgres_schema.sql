-- PostgreSQL Schema for GOAT Talent Management System

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS centers (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
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
    organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
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
    exposure_data TEXT,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
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
    timing_data TEXT,           -- JSON; session+question timing for research & AI analytics
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
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
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

-- ═══════════════════════════════════════════════════════════════════════════════
-- ARTSPARK — Gamified Adaptive Psychometric Module (Creative & Artistic)
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS artspark_item_bank (
    id          SERIAL PRIMARY KEY,
    item_uuid   VARCHAR(64) UNIQUE NOT NULL,
    domain      VARCHAR(50) NOT NULL,      -- visual_art | music | storytelling | drama | dance_movement | craft_design
    tier        VARCHAR(20) NOT NULL,      -- easy | medium | hard | expert
    difficulty  REAL NOT NULL DEFAULT 0.0, -- IRT b-parameter (-2 to +2)
    q_type      VARCHAR(30) NOT NULL,      -- image_choice | likert | open_text | sequence | match_pair
    prompt      TEXT NOT NULL,
    options     TEXT,                      -- JSON array for choice/sequence types
    correct_key TEXT,                      -- answer key for auto-scored types
    explanation TEXT,
    tags        TEXT,                      -- JSON array of skill tags
    language    VARCHAR(10) DEFAULT 'en',
    active      INTEGER DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artspark_sessions (
    id                  SERIAL PRIMARY KEY,
    session_uuid        VARCHAR(64) UNIQUE NOT NULL,
    child_id            INTEGER REFERENCES children(id) ON DELETE SET NULL,
    student_id          INTEGER,           -- mirrors child_id for anonymous sessions
    facilitator_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    language            VARCHAR(10) DEFAULT 'en',
    status              VARCHAR(20) DEFAULT 'in_progress', -- in_progress | completed | abandoned
    domain_order        TEXT,              -- JSON array: domains selected/order
    current_domain_idx  INTEGER DEFAULT 0,
    current_q_idx       INTEGER DEFAULT 0,
    theta               TEXT,              -- JSON map domain->theta float
    medals              TEXT,              -- JSON map domain->bronze|silver|gold|platinum
    xp_total            INTEGER DEFAULT 0,
    streak_max          INTEGER DEFAULT 0,
    questions_answered  INTEGER DEFAULT 0,
    raw_item_trail      TEXT,              -- JSON array of {item_uuid, response, correct, theta_after}
    start_ts            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_ts              TIMESTAMP,
    total_duration_ms   INTEGER,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS artspark_responses (
    id              SERIAL PRIMARY KEY,
    session_uuid    VARCHAR(64) NOT NULL,
    item_uuid       VARCHAR(64) NOT NULL,
    domain          VARCHAR(50) NOT NULL,
    tier            VARCHAR(20) NOT NULL,
    difficulty      REAL,
    q_type          VARCHAR(30),
    response_value  TEXT,                  -- raw answer (option key / likert int / text)
    is_correct      INTEGER,               -- 1 | 0 | NULL (open_text not auto-scored)
    response_ms     INTEGER,               -- latency in ms
    theta_before    REAL,
    theta_after     REAL,
    xp_earned       INTEGER DEFAULT 0,
    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
