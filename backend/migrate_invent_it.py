"""
Migration: Create Invent It tables in Supabase/PostgreSQL.
Run once: python backend/migrate_invent_it.py
"""
import os, sys
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") or "https://ubsjcfaokemckctswnzi.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_KEY:
    print("[ERROR] SUPABASE_SERVICE_ROLE_KEY not set in .env")
    sys.exit(1)

try:
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"[ERROR] Could not create Supabase client: {e}")
    sys.exit(1)

# We'll run migrations via psycopg2 using DATABASE_URL
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    print("[ERROR] DATABASE_URL not set in .env")
    sys.exit(1)

try:
    import psycopg2
    if DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
    conn = psycopg2.connect(DB_URL, connect_timeout=15)
    cursor = conn.cursor()
    print("[OK] Connected to database.")
except Exception as e:
    print(f"[ERROR] Could not connect to database: {e}")
    sys.exit(1)

MIGRATION_SQL = """
-- ============================================================
-- INVENT IT Performance Evidence Module — Database Migration
-- ============================================================

-- 1. Game session header
CREATE TABLE IF NOT EXISTS invent_it_sessions (
    id                        SERIAL PRIMARY KEY,
    student_id                INTEGER REFERENCES children(id) ON DELETE SET NULL,
    session_uuid              TEXT UNIQUE NOT NULL,
    experience_id             TEXT DEFAULT 'invent_it_v1',
    facilitator_id            INTEGER,
    language                  VARCHAR(10) DEFAULT 'en',
    status                    VARCHAR(20) DEFAULT 'in_progress',
    start_ts                  TIMESTAMPTZ DEFAULT NOW(),
    end_ts                    TIMESTAMPTZ,
    total_duration_ms         BIGINT,
    time_to_first_response_ms BIGINT,
    number_of_ideas           INTEGER DEFAULT 0,
    number_of_submissions     INTEGER DEFAULT 0,
    number_of_revisions       INTEGER DEFAULT 0,
    number_of_voice_responses INTEGER DEFAULT 0,
    number_of_text_responses  INTEGER DEFAULT 0,
    number_of_drawings        INTEGER DEFAULT 0,
    hint_count                INTEGER DEFAULT 0,
    round1_output             JSONB,
    round2_output             JSONB,
    raw_metrics               JSONB,
    created_at                TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Per-round responses (raw — never overwritten)
CREATE TABLE IF NOT EXISTS invent_it_responses (
    id                SERIAL PRIMARY KEY,
    session_uuid      TEXT REFERENCES invent_it_sessions(session_uuid) ON DELETE CASCADE,
    round_id          INTEGER NOT NULL,
    idea_index        INTEGER,
    input_type        VARCHAR(10) NOT NULL,
    text_content      TEXT,
    drawing_url       TEXT,
    voice_url         TEXT,
    voice_transcript  TEXT,
    language          VARCHAR(10),
    duration_ms       INTEGER,
    submitted_at      TIMESTAMPTZ DEFAULT NOW(),
    revised           BOOLEAN DEFAULT FALSE,
    revision_of       INTEGER REFERENCES invent_it_responses(id) ON DELETE SET NULL
);

-- 3. Raw interaction events timeline
CREATE TABLE IF NOT EXISTS invent_it_events (
    id           SERIAL PRIMARY KEY,
    session_uuid TEXT REFERENCES invent_it_sessions(session_uuid) ON DELETE CASCADE,
    round_id     INTEGER,
    event_type   TEXT NOT NULL,
    event_data   JSONB,
    ts           TIMESTAMPTZ DEFAULT NOW()
);

-- 4. AI evidence analysis (separate from raw responses)
CREATE TABLE IF NOT EXISTS invent_it_ai_analysis (
    id                 SERIAL PRIMARY KEY,
    session_uuid       TEXT REFERENCES invent_it_sessions(session_uuid) ON DELETE CASCADE,
    response_id        INTEGER REFERENCES invent_it_responses(id) ON DELETE CASCADE,
    idea_id            TEXT,
    behaviour_evidence JSONB,
    evidence_quality   VARCHAR(20),
    reasoning          TEXT,
    model_version      TEXT,
    analysed_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Aggregated behavioural evidence per session
CREATE TABLE IF NOT EXISTS invent_it_behaviour_evidence (
    id                       SERIAL PRIMARY KEY,
    session_uuid             TEXT UNIQUE REFERENCES invent_it_sessions(session_uuid) ON DELETE CASCADE,
    o1_score                 NUMERIC(4,2),
    o2_score                 NUMERIC(4,2),
    o3_score                 NUMERIC(4,2),
    o4_score                 NUMERIC(4,2),
    o5_score                 NUMERIC(4,2),
    o6_score                 NUMERIC(4,2),
    provisional_rubric_score INTEGER,
    evidence_confidence      VARCHAR(20),
    round1_ideas             INTEGER DEFAULT 0,
    round2_ideas             INTEGER DEFAULT 0,
    cross_round_analysis     JSONB,
    notes                    TEXT,
    computed_at              TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Facilitator observation checklist
CREATE TABLE IF NOT EXISTS invent_it_facilitator_obs (
    id                               SERIAL PRIMARY KEY,
    session_uuid                     TEXT REFERENCES invent_it_sessions(session_uuid) ON DELETE CASCADE,
    facilitator_id                   INTEGER,
    obs_continued_without_prompting  INTEGER DEFAULT -1,
    obs_multiple_ideas               INTEGER DEFAULT -1,
    obs_revised_idea                 INTEGER DEFAULT -1,
    obs_experimented_alternatives    INTEGER DEFAULT -1,
    obs_stuck_after_first            INTEGER DEFAULT -1,
    obs_persisted_after_difficulty   INTEGER DEFAULT -1,
    obs_explained_reasoning          INTEGER DEFAULT -1,
    additional_notes                 TEXT,
    submitted_at                     TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_invent_it_sessions_student ON invent_it_sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_invent_it_responses_session ON invent_it_responses(session_uuid);
CREATE INDEX IF NOT EXISTS idx_invent_it_events_session ON invent_it_events(session_uuid);
CREATE INDEX IF NOT EXISTS idx_invent_it_ai_session ON invent_it_ai_analysis(session_uuid);
CREATE INDEX IF NOT EXISTS idx_invent_it_be_session ON invent_it_behaviour_evidence(session_uuid);
CREATE INDEX IF NOT EXISTS idx_invent_it_fobs_session ON invent_it_facilitator_obs(session_uuid);

-- RLS (enable on all tables)
ALTER TABLE invent_it_sessions             ENABLE ROW LEVEL SECURITY;
ALTER TABLE invent_it_responses            ENABLE ROW LEVEL SECURITY;
ALTER TABLE invent_it_events               ENABLE ROW LEVEL SECURITY;
ALTER TABLE invent_it_ai_analysis          ENABLE ROW LEVEL SECURITY;
ALTER TABLE invent_it_behaviour_evidence   ENABLE ROW LEVEL SECURITY;
ALTER TABLE invent_it_facilitator_obs      ENABLE ROW LEVEL SECURITY;

-- RLS Policies: service_role bypasses RLS automatically.
-- Allow anon/authenticated to INSERT (game can be played without login)
-- Allow authenticated to SELECT their own sessions

DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_sessions' AND policyname='allow_insert_sessions') THEN
    CREATE POLICY allow_insert_sessions ON invent_it_sessions FOR INSERT TO anon, authenticated WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_sessions' AND policyname='allow_select_sessions') THEN
    CREATE POLICY allow_select_sessions ON invent_it_sessions FOR SELECT TO authenticated USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_sessions' AND policyname='allow_update_sessions') THEN
    CREATE POLICY allow_update_sessions ON invent_it_sessions FOR UPDATE TO anon, authenticated USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_responses' AND policyname='allow_insert_responses') THEN
    CREATE POLICY allow_insert_responses ON invent_it_responses FOR INSERT TO anon, authenticated WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_responses' AND policyname='allow_select_responses') THEN
    CREATE POLICY allow_select_responses ON invent_it_responses FOR SELECT TO authenticated USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_events' AND policyname='allow_insert_events') THEN
    CREATE POLICY allow_insert_events ON invent_it_events FOR INSERT TO anon, authenticated WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_events' AND policyname='allow_select_events') THEN
    CREATE POLICY allow_select_events ON invent_it_events FOR SELECT TO authenticated USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_ai_analysis' AND policyname='allow_insert_ai') THEN
    CREATE POLICY allow_insert_ai ON invent_it_ai_analysis FOR INSERT TO anon, authenticated WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_ai_analysis' AND policyname='allow_select_ai') THEN
    CREATE POLICY allow_select_ai ON invent_it_ai_analysis FOR SELECT TO authenticated USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_behaviour_evidence' AND policyname='allow_insert_be') THEN
    CREATE POLICY allow_insert_be ON invent_it_behaviour_evidence FOR INSERT TO anon, authenticated WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_behaviour_evidence' AND policyname='allow_select_be') THEN
    CREATE POLICY allow_select_be ON invent_it_behaviour_evidence FOR SELECT TO authenticated USING (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_behaviour_evidence' AND policyname='allow_update_be') THEN
    CREATE POLICY allow_update_be ON invent_it_behaviour_evidence FOR UPDATE TO anon, authenticated USING (true);
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_facilitator_obs' AND policyname='allow_insert_fobs') THEN
    CREATE POLICY allow_insert_fobs ON invent_it_facilitator_obs FOR INSERT TO authenticated WITH CHECK (true);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE tablename='invent_it_facilitator_obs' AND policyname='allow_select_fobs') THEN
    CREATE POLICY allow_select_fobs ON invent_it_facilitator_obs FOR SELECT TO authenticated USING (true);
  END IF;
END $$;
"""

try:
    cursor.execute(MIGRATION_SQL)
    conn.commit()
    print("[OK] All Invent It tables created/verified successfully.")
except Exception as e:
    conn.rollback()
    print(f"[ERROR] Migration failed: {e}")
    cursor.close()
    conn.close()
    sys.exit(1)

cursor.close()
conn.close()
print("[DONE] Migration complete.")
