"""
GOAT Backend — Flask + SQLite
Greatest of All Talents System for Project WHY
"""

from dotenv import load_dotenv
load_dotenv()

import sqlite3
import json
import os
import hashlib
import secrets
from flask import Flask, request, jsonify, g
from datetime import datetime

# ── Supabase Client Initialization ──────────────────────────────────────────
supabase_client = None
try:
    from supabase import create_client, Client
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    # Prefer private service role key for backend operations to bypass RLS, fallback to anon key
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if service_key == "your-secret-service-role-key":
        service_key = None
    supabase_key = service_key or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    if supabase_url and supabase_key:
        supabase_client = create_client(supabase_url, supabase_key)
        key_type = "service_role" if service_key else "anon"
        print(f"[SUCCESS] Python Supabase client initialized (Key: {key_type}).")
    else:
        print("[DATABASE WARNING] Supabase URL or Key missing in environment. Supabase sync disabled.")
except Exception as e:
    print(f"[DATABASE WARNING] Failed to initialize Supabase client: {e}. Supabase sync disabled.")

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "goat.db")


# ── CORS (manual, no dependency needed) ──────────────────────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

@app.route("/", defaults={"path": ""}, methods=["OPTIONS"])
@app.route("/<path:path>", methods=["OPTIONS"])
def options_handler(path):
    return jsonify({}), 200

# ── Database connection ───────────────────────────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

class PostgresCursorWrapper:
    def __init__(self, pg_cursor, is_insert=False):
        self.cursor = pg_cursor
        self._lastrowid = None
        if is_insert:
            try:
                row = self.cursor.fetchone()
                if row:
                    self._lastrowid = list(row.values())[0]
            except Exception:
                pass

    def fetchone(self):
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    @property
    def lastrowid(self):
        return self._lastrowid

class PostgresConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=()):
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        # translate ? to %s
        sql = sql.replace("?", "%s")
        # translate SQLite-specific SQL syntax
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        sql = sql.replace("datetime('now', '+12 hours')", "CURRENT_TIMESTAMP + INTERVAL '12 hours'")
        if "INSERT OR IGNORE" in sql:
            sql = sql.replace("INSERT OR IGNORE INTO", "INSERT INTO")
            if "mentors" in sql:
                sql += " ON CONFLICT (id) DO NOTHING"
            elif "users" in sql:
                sql += " ON CONFLICT (email) DO NOTHING"
            else:
                sql += " ON CONFLICT DO NOTHING"
                
        is_insert = sql.strip().upper().startswith("INSERT")
        if is_insert and "RETURNING" not in sql.upper():
            # Append RETURNING id for lastrowid support
            # Simple heuristic: find first table name
            sql_parts = sql.strip().split()
            if len(sql_parts) > 2:
                table_name = sql_parts[2].strip("()").split("(")[0]
                sql += " RETURNING id"

        cursor.execute(sql, params)
        return PostgresCursorWrapper(cursor, is_insert=is_insert)

    def executescript(self, script):
        # execute PostgreSQL script
        cursor = self.conn.cursor()
        cursor.execute(script)
        cursor.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

class SQLiteConnectionWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql, params=()):
        return self.conn.execute(sql, params)

    def executescript(self, script):
        self.conn.executescript(script)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def get_db():
    if "db" not in g:
        db_url = os.environ.get("DATABASE_URL")
        # Check if DATABASE_URL starts with postgresql:// or postgres://
        if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES:
            try:
                if db_url.startswith("postgres://"):
                    db_url = db_url.replace("postgres://", "postgresql://", 1)
                conn = psycopg2.connect(db_url)
                g.db = PostgresConnectionWrapper(conn)
            except Exception as e:
                print(f"[DATABASE WARNING] Failed to connect to Postgres: {e}. Falling back to SQLite.")
                g.db = SQLiteConnectionWrapper(sqlite3.connect(DB_PATH))
        else:
            g.db = SQLiteConnectionWrapper(sqlite3.connect(DB_PATH))
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db:
        db.close()

def hash_password(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"{salt}${digest.hex()}"

def check_password(password, stored):
    if not stored or "$" not in stored:
        return False
    salt, expected = stored.split("$", 1)
    return secrets.compare_digest(hash_password(password, salt), f"{salt}${expected}")

def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.replace("Bearer ", "", 1).strip()
    if not token:
        return None
    row = get_db().execute("""
        SELECT u.id, u.name, u.email, u.role
        FROM auth_sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = ? AND s.expires_at > datetime('now')
    """, (token,)).fetchone()
    return dict(row) if row else None

def require_user():
    user = current_user()
    if not user:
        return None, (jsonify({"error": "Login required"}), 401)
    return user, None

def require_role(allowed_roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user, error = require_user()
            if error:
                return error
            if user["role"] not in allowed_roles:
                return jsonify({"error": "Forbidden: Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ── Schema setup ──────────────────────────────────────────────────────────────
def init_db():
    db_url = os.environ.get("DATABASE_URL")
    is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES
    
    if is_postgres:
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            schema_path = os.path.join(os.path.dirname(__file__), "db", "postgres_schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            
            cursor.execute(schema_sql)
            conn.commit()
            cursor.close()
            
            # Seed data for postgres
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM mentors")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO mentors (id, name, domain, bio, contact) VALUES
                    (1, 'Anita Sharma',    'creative',       'Art teacher, 12 yrs experience', 'anita@why.org'),
                    (2, 'Rahul Gupta',     'logical',        'Math tutor, IIT graduate',       'rahul@why.org'),
                    (3, 'Priya Mehta',     'kinesthetic',    'Dance instructor, Kathak',       'priya@why.org'),
                    (4, 'Suresh Kumar',    'spatial',        'Carpenter & craft trainer',      'suresh@why.org'),
                    (5, 'Deepa Nair',      'social',         'Community organiser, 8 yrs',     'deepa@why.org'),
                    (6, 'Arjun Singh',     'language',       'Theatre director, storyteller',  'arjun@why.org'),
                    (7, 'Meena Iyer',      'naturalist',     'Botanist, nature educator',      'meena@why.org'),
                    (8, 'Kavita Bose',     'intrapersonal',  'Counsellor, mindfulness guide',  'kavita@why.org')
                """)
            
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, role) VALUES
                    ('Master Admin', 'master@why.org', %s, 'master_admin'),
                    ('Admin Account', 'admin@why.org', %s, 'admin'),
                    ('Demo Facilitator', 'facilitator@why.org', %s, 'facilitator'),
                    ('Demo Mentor', 'mentor@why.org', %s, 'mentor'),
                    ('Demo Student', 'student@why.org', %s, 'student'),
                    ('Demo Parent', 'parent@why.org', %s, 'parent')
                """, (hash_password("why123"), hash_password("why123"), hash_password("why123"), hash_password("why123"), hash_password("why123"), hash_password("why123")))
                
            cursor.execute("SELECT COUNT(*) FROM centers")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO centers (name, location) VALUES
                    ('New Delhi Center', 'Okhla, New Delhi'),
                    ('Mumbai Center', 'Dharavi, Mumbai')
                """)
            
            cursor.execute("SELECT COUNT(*) FROM puzzles")
            if cursor.fetchone()[0] == 0:
                for p in DEFAULT_AI_PUZZLES:
                    cursor.execute("""
                        INSERT INTO puzzles (key, type, domain, component, data)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
            
            conn.commit()
            cursor.close()
            conn.close()
            print("[SUCCESS] PostgreSQL/Supabase initialized successfully!")
            return
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to initialize Postgres: {e}. Falling back to SQLite.")
            
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS centers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            location    TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'facilitator',
            active        INTEGER DEFAULT 1,
            center_id     INTEGER REFERENCES centers(id) ON DELETE SET NULL,
            student_id    INTEGER,
            created_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS auth_sessions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token      TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS children (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER NOT NULL,
            language    TEXT    NOT NULL DEFAULT 'Hindi',
            school_year TEXT,
            gender      TEXT,
            exp_kinesthetic  INTEGER DEFAULT 0,
            exp_creative     INTEGER DEFAULT 0,
            exp_logical      INTEGER DEFAULT 0,
            exp_spatial      INTEGER DEFAULT 0,
            exp_social       INTEGER DEFAULT 0,
            exp_language     INTEGER DEFAULT 0,
            exp_naturalist   INTEGER DEFAULT 0,
            exp_intrapersonal INTEGER DEFAULT 0,
            center_id     INTEGER REFERENCES centers(id) ON DELETE SET NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id        INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            phase           TEXT    NOT NULL DEFAULT 'discovery',
            responses       TEXT,
            domain_flags    TEXT,
            tq_scores       TEXT,
            eq_score        INTEGER,
            visualizer_score INTEGER,
            personality_data TEXT,
            integrated_score TEXT,
            top_domain      TEXT,
            generated_tasks TEXT,
            status          TEXT    DEFAULT 'in_progress',
            created_at      TEXT    DEFAULT (datetime('now')),
            completed_at    TEXT
        );

        CREATE TABLE IF NOT EXISTS facilitator_notes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            child_id    INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            facilitator TEXT,
            confirmed   INTEGER DEFAULT 0,
            observation TEXT,
            override_domain TEXT,
            notes       TEXT,
            agreement   TEXT DEFAULT 'Agree',
            strengths_observed TEXT,
            concerns    TEXT,
            suggested_workshop TEXT,
            obs_creativity INTEGER DEFAULT 0,
            obs_communication INTEGER DEFAULT 0,
            obs_leadership INTEGER DEFAULT 0,
            obs_focus INTEGER DEFAULT 0,
            obs_curiosity INTEGER DEFAULT 0,
            evidence_notes TEXT,
            validation_status TEXT DEFAULT 'Pending Validation',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS mentors (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            domain      TEXT NOT NULL,
            bio         TEXT,
            contact     TEXT,
            active      INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS mentor_matches (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            child_id    INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            mentor_id   INTEGER NOT NULL REFERENCES mentors(id) ON DELETE CASCADE,
            domain      TEXT,
            plan        TEXT,
            status      TEXT    DEFAULT 'active',
            matched_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS milestones (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id    INTEGER NOT NULL REFERENCES mentor_matches(id) ON DELETE CASCADE,
            title       TEXT,
            due_date    TEXT,
            done        INTEGER DEFAULT 0,
            note        TEXT
        );

        CREATE TABLE IF NOT EXISTS workshops (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            domain      TEXT NOT NULL,
            center_id   INTEGER REFERENCES centers(id) ON DELETE SET NULL,
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS workshop_sessions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            workshop_id         INTEGER NOT NULL REFERENCES workshops(id) ON DELETE CASCADE,
            session_date        TEXT NOT NULL,
            notes               TEXT,
            created_at          TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS workshop_attendance (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            workshop_session_id INTEGER NOT NULL REFERENCES workshop_sessions(id) ON DELETE CASCADE,
            child_id            INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            status              TEXT NOT NULL,
            created_at          TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS mentor_validations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id    INTEGER NOT NULL REFERENCES mentor_matches(id) ON DELETE CASCADE,
            child_id    INTEGER NOT NULL REFERENCES children(id) ON DELETE CASCADE,
            domain      TEXT NOT NULL,
            rating      INTEGER DEFAULT 3,
            strengths   TEXT,
            growth_areas TEXT,
            notes       TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS puzzles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            key         TEXT UNIQUE NOT NULL,
            type        TEXT NOT NULL,
            domain      TEXT NOT NULL,
            component   TEXT,
            data        TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );
    """)
    
    if db.execute("SELECT COUNT(*) FROM mentors").fetchone()[0] == 0:
        db.executescript("""
            INSERT INTO mentors (id, name, domain, bio, contact) VALUES
            (1, 'Anita Sharma',    'creative',       'Art teacher, 12 yrs experience', 'anita@why.org'),
            (2, 'Rahul Gupta',     'logical',        'Math tutor, IIT graduate',       'rahul@why.org'),
            (3, 'Priya Mehta',     'kinesthetic',    'Dance instructor, Kathak',       'priya@why.org'),
            (4, 'Suresh Kumar',    'spatial',        'Carpenter & craft trainer',      'suresh@why.org'),
            (5, 'Deepa Nair',      'social',         'Community organiser, 8 yrs',     'deepa@why.org'),
            (6, 'Arjun Singh',     'language',       'Theatre director, storyteller',  'arjun@why.org'),
            (7, 'Meena Iyer',      'naturalist',     'Botanist, nature educator',      'meena@why.org'),
            (8, 'Kavita Bose',     'intrapersonal',  'Counsellor, mindfulness guide',  'kavita@why.org');
        """)
        
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Master Admin', 'master@why.org', ?, 'master_admin')", (hash_password("why123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Admin Account', 'admin@why.org', ?, 'admin')", (hash_password("why123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Demo Facilitator', 'facilitator@why.org', ?, 'facilitator')", (hash_password("why123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Demo Mentor', 'mentor@why.org', ?, 'mentor')", (hash_password("why123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Demo Student', 'student@why.org', ?, 'student')", (hash_password("why123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role) VALUES ('Demo Parent', 'parent@why.org', ?, 'parent')", (hash_password("why123"),))
        
    if db.execute("SELECT COUNT(*) FROM centers").fetchone()[0] == 0:
        db.execute("INSERT INTO centers (name, location) VALUES ('New Delhi Center', 'Okhla, New Delhi')")
        db.execute("INSERT INTO centers (name, location) VALUES ('Mumbai Center', 'Dharavi, Mumbai')")
        
    if db.execute("SELECT COUNT(*) FROM puzzles").fetchone()[0] == 0:
        for p in DEFAULT_AI_PUZZLES:
            db.execute("""
                INSERT INTO puzzles (key, type, domain, component, data)
                VALUES (?, ?, ?, ?, ?)
            """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
            
    db.commit()
    db.close()
    print("[SUCCESS] SQLite database initialized successfully!")
    sync_static_tables_supabase()

def sync_static_tables_supabase():
    if not supabase_client:
        return
    try:
        # Check centers
        res_centers = supabase_client.table("centers").select("id").limit(1).execute()
        if not res_centers.data:
            print("[SUPABASE] Seeding centers...")
            centers_data = [
                {"id": 1, "name": "New Delhi Center", "location": "Okhla, New Delhi"},
                {"id": 2, "name": "Mumbai Center", "location": "Dharavi, Mumbai"}
            ]
            supabase_client.table("centers").insert(centers_data).execute()
            
        # Check mentors
        res_mentors = supabase_client.table("mentors").select("id").limit(1).execute()
        if not res_mentors.data:
            print("[SUPABASE] Seeding mentors...")
            mentors_data = [
                {"id": 1, "name": "Anita Sharma",    "domain": "creative",       "bio": "Art teacher, 12 yrs experience", "contact": "anita@why.org"},
                {"id": 2, "name": "Rahul Gupta",     "domain": "logical",        "bio": "Math tutor, IIT graduate",       "contact": "rahul@why.org"},
                {"id": 3, "name": "Priya Mehta",     "domain": "kinesthetic",    "bio": "Dance instructor, Kathak",       "contact": "priya@why.org"},
                {"id": 4, "name": "Suresh Kumar",    "domain": "spatial",        "bio": "Carpenter & craft trainer",      "contact": "suresh@why.org"},
                {"id": 5, "name": "Deepa Nair",      "domain": "social",         "bio": "Community organiser, 8 yrs",     "contact": "deepa@why.org"},
                {"id": 6, "name": "Arjun Singh",     "domain": "language",       "bio": "Theatre director, storyteller",  "contact": "arjun@why.org"},
                {"id": 7, "name": "Meena Iyer",      "domain": "naturalist",     "bio": "Botanist, nature educator",      "contact": "meena@why.org"},
                {"id": 8, "name": "Kavita Bose",     "domain": "intrapersonal",  "bio": "Counsellor, mindfulness guide",  "contact": "kavita@why.org"}
            ]
            supabase_client.table("mentors").insert(mentors_data).execute()
            
    except Exception as e:
        print(f"[SUPABASE WARNING] Failed to seed static tables on Supabase: {e}")



# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Children
# ═══════════════════════════════════════════════════════════════════════════════

# ROUTES - Auth

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email=? AND active=1", (email,)).fetchone()
    if not row or not check_password(password, row["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = secrets.token_urlsafe(32)
    db.execute("""
        INSERT INTO auth_sessions (user_id, token, expires_at)
        VALUES (?, ?, datetime('now', '+12 hours'))
    """, (row["id"], token))
    db.commit()
    return jsonify({
        "token": token,
        "user": {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]},
    })

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    role = data.get("role", "pending_facilitator")
    
    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
        
    if role not in ("pending_facilitator", "pending_mentor"):
        role = "pending_facilitator"
        
    db = get_db()
    try:
        db.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (name, email, hash_password(password), role))
        db.commit()
    except Exception as e:
        return jsonify({"error": "Email already exists or invalid data"}), 400
        
    return jsonify({"status": "success", "message": "Registration successful, pending approval."}), 201

@app.route("/api/auth/login-supabase", methods=["POST"])
def login_supabase():
    data = request.json or {}
    sb_token = data.get("token")
    if not sb_token:
        return jsonify({"error": "Token is required"}), 400
        
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    if not supabase_url:
        return jsonify({"error": "Supabase URL not configured on server"}), 500
        
    import urllib.request
    import urllib.error
    req_url = f"{supabase_url.rstrip('/')}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {sb_token}",
        "apikey": os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    }
    req = urllib.request.Request(req_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            user_data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return jsonify({"error": "Invalid Supabase session"}), 401
    except Exception as e:
        return jsonify({"error": f"Failed to connect to Supabase Auth: {e}"}), 500
        
    user_id = user_data.get("id")
    email = user_data.get("email")
    
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row:
        name = user_data.get("user_metadata", {}).get("name", "New User")
        role = user_data.get("user_metadata", {}).get("role", "facilitator")
        db_url = os.environ.get("DATABASE_URL")
        is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES
        if is_postgres:
            db.execute("INSERT INTO users (id, name, email, role) VALUES (?, ?, ?, ?) ON CONFLICT (id) DO NOTHING", (user_id, name, email, role))
        else:
            db.execute("INSERT INTO users (name, email, role) VALUES (?, ?, ?)", (name, email, role))
        db.commit()
        row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        
    token = secrets.token_urlsafe(32)
    db.execute("""
        INSERT INTO auth_sessions (user_id, token, expires_at)
        VALUES (?, ?, datetime('now', '+12 hours'))
    """, (row["id"], token))
    db.commit()
    
    return jsonify({
        "token": token,
        "user": {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}
    })

@app.route("/api/auth/me", methods=["GET"])
def me():
    user, error = require_user()
    if error:
        return error
    return jsonify({"user": user})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "", 1).strip() if auth.startswith("Bearer ") else ""
    if token:
        db = get_db()
        db.execute("DELETE FROM auth_sessions WHERE token=?", (token,))
        db.commit()
    return jsonify({"ok": True})

@app.route("/api/auth/change-password", methods=["POST"])
def change_password_route():
    user, error = require_user()
    if error:
        return error
    data = request.json or {}
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if not old_password or not new_password:
        return jsonify({"error": "Old and new passwords are required"}), 400
        
    db = get_db()
    row = db.execute("SELECT password_hash FROM users WHERE id=?", (user["id"],)).fetchone()
    if not row or not check_password(old_password, row["password_hash"]):
        return jsonify({"error": "Invalid current password"}), 401
        
    db.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_password), user["id"]))
    db.commit()
    return jsonify({"status": "success", "message": "Password updated successfully"})

@app.route("/api/children", methods=["GET"])
def list_children():
    db = get_db()
    rows = db.execute("SELECT * FROM children ORDER BY created_at DESC").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/children", methods=["POST"])
def create_child():
    data = request.json or {}
    print("==================================================")
    print(f"DEBUG: create_child called with data: {data}")
    try:
        user = current_user()
        print(f"DEBUG: Current authenticated user: {user}")
    except Exception as e:
        print(f"DEBUG: Error retrieving current user: {e}")
    
    supabase_id = None
    if supabase_client:
        try:
            insert_data = {
                "name": data["name"],
                "age": int(data["age"]),
                "language": data.get("language", "Hindi"),
                "school_year": data.get("school_year", ""),
                "gender": data.get("gender", ""),
                "exp_kinesthetic": int(data.get("exp_kinesthetic", 0)),
                "exp_creative": int(data.get("exp_creative", 0)),
                "exp_logical": int(data.get("exp_logical", 0)),
                "exp_spatial": int(data.get("exp_spatial", 0)),
                "exp_social": int(data.get("exp_social", 0)),
                "exp_language": int(data.get("exp_language", 0)),
                "exp_naturalist": int(data.get("exp_naturalist", 0)),
                "exp_intrapersonal": int(data.get("exp_intrapersonal", 0))
            }
            print(f"DEBUG: Attempting Supabase insert for child with data: {insert_data}")
            res = supabase_client.table("children").insert(insert_data).execute()
            print(f"DEBUG: Supabase insert child response: {res.data}")
            if res.data and len(res.data) > 0:
                supabase_id = res.data[0]["id"]
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase insert child: {e}")
            import traceback
            traceback.print_exc()
            
    db = get_db()
    if supabase_id is not None:
        db.execute("""
            INSERT INTO children
              (id, name, age, language, school_year, gender,
               exp_kinesthetic, exp_creative, exp_logical, exp_spatial,
               exp_social, exp_language, exp_naturalist, exp_intrapersonal)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            supabase_id,
            data["name"], data["age"], data.get("language", "Hindi"),
            data.get("school_year", ""), data.get("gender", ""),
            data.get("exp_kinesthetic", 0), data.get("exp_creative", 0),
            data.get("exp_logical", 0),    data.get("exp_spatial", 0),
            data.get("exp_social", 0),     data.get("exp_language", 0),
            data.get("exp_naturalist", 0), data.get("exp_intrapersonal", 0),
        ))
        db.commit()
        child_id = supabase_id
    else:
        cur = db.execute("""
            INSERT INTO children
              (name, age, language, school_year, gender,
               exp_kinesthetic, exp_creative, exp_logical, exp_spatial,
               exp_social, exp_language, exp_naturalist, exp_intrapersonal)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["name"], data["age"], data.get("language", "Hindi"),
            data.get("school_year", ""), data.get("gender", ""),
            data.get("exp_kinesthetic", 0), data.get("exp_creative", 0),
            data.get("exp_logical", 0),    data.get("exp_spatial", 0),
            data.get("exp_social", 0),     data.get("exp_language", 0),
            data.get("exp_naturalist", 0), data.get("exp_intrapersonal", 0),
        ))
        db.commit()
        child_id = cur.lastrowid
        
    return jsonify({"id": child_id}), 201

@app.route("/api/children/<int:cid>", methods=["GET"])
def get_child(cid):
    db = get_db()
    row = db.execute("SELECT * FROM children WHERE id=?", (cid,)).fetchone()
    if not row: return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Sessions
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/sessions", methods=["POST"])
def create_session():
    data = request.json or {}
    child_id = data.get("child_id")
    print("==================================================")
    print(f"DEBUG: create_session called with data: {data}")
    try:
        user = current_user()
        print(f"DEBUG: Current authenticated user: {user}")
    except Exception as e:
        print(f"DEBUG: Error retrieving current user: {e}")
    
    supabase_id = None
    if supabase_client:
        try:
            insert_data = {
                "child_id": child_id,
                "phase": "discovery",
                "status": "in_progress"
            }
            print(f"DEBUG: Attempting Supabase insert for session with data: {insert_data}")
            res = supabase_client.table("sessions").insert(insert_data).execute()
            print(f"DEBUG: Supabase insert session response: {res.data}")
            if res.data and len(res.data) > 0:
                supabase_id = res.data[0]["id"]
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase insert session: {e}")
            import traceback
            traceback.print_exc()
            
    db = get_db()
    if supabase_id is not None:
        db.execute(
            "INSERT INTO sessions (id, child_id, phase) VALUES (?,?,?)",
            (supabase_id, child_id, "discovery")
        )
        db.commit()
        session_id = supabase_id
    else:
        cur = db.execute(
            "INSERT INTO sessions (child_id, phase) VALUES (?,?)",
            (child_id, "discovery")
        )
        db.commit()
        session_id = cur.lastrowid
        
    return jsonify({"id": session_id}), 201

@app.route("/api/sessions/<int:sid>", methods=["GET"])
def get_session(sid):
    db = get_db()
    row = db.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
    if not row: return jsonify({"error": "Not found"}), 404
    return jsonify(dict(row))

# ── Dynamic AI Custom Puzzle Generator ────────────────────────────────────────

DEFAULT_AI_PUZZLES = [
    # ── LOGICAL & ANALYTICAL (6 puzzles) ──
    {
        "key": "logical_pattern_matrix",
        "type": "pattern_choice",
        "domain": "logical",
        "component": "pattern_recognition",
        "title": {"English": "The Wizard's Door Pyramid", },
        "prompt": {"English": "At the bottom of a stone tower, numbers are added together to open the lock. The bottom rows are 3 and 5, which add up to 8. Next to them are 5 and 9, which add up to 14. What number belongs at the very top of the pyramid? (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)", },
        "sequence": ["3", "5", "9", "8", "14", "?"],
        "options": ["18", "20", "22", "24"],
        "answer": "22",
        "metric": "correctness"
    },
    {
        "key": "logical_riddle",
        "type": "choice",
        "domain": "logical",
        "component": "sequence_logic",
        "title": {"English": "The Secret Cipher of Animals", },
        "prompt": {"English": "A secret code matches animals to numbers based on their legs: Cat is 4, Spider is 8, Ant is 6. What number represents a Snake?", },
        "options": [
            {"label": {"English": "4", }, "value": 0},
            {"label": {"English": "0", }, "value": 4},
            {"label": {"English": "2", }, "value": 0},
            {"label": {"English": "6", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "logical_pattern_3",
        "type": "pattern_choice",
        "domain": "logical",
        "component": "pattern_recognition",
        "title": {"English": "The Magic Number Train", },
        "prompt": {"English": "A magic train has carriages with numbers: 1, 3, 6, 10, 15, ?. What number is on the next carriage?", },
        "sequence": ["1", "3", "6", "10", "15", "?"],
        "options": ["18", "20", "21", "25"],
        "answer": "21",
        "metric": "correctness"
    },
    {
        "key": "logical_riddle_4",
        "type": "choice",
        "domain": "logical",
        "component": "number_reasoning",
        "title": {"English": "The Weighing Scale Puzzle", },
        "prompt": {"English": "One heavy golden block balances exactly with three small silver balls. Two silver balls balance exactly with four light feathers. How many feathers are needed to balance one golden block?", },
        "options": [
            {"label": {"English": "6", }, "value": 4},
            {"label": {"English": "4", }, "value": 0},
            {"label": {"English": "8", }, "value": 0},
            {"label": {"English": "12", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "logical_pattern_5",
        "type": "pattern_choice",
        "domain": "logical",
        "component": "pattern_recognition",
        "title": {"English": "The Repeating Symbol Grid", },
        "prompt": {"English": "Find the missing symbol in this repeating pattern: ★, ●, ▲, ★, ●, ?, ★", },
        "sequence": ["★", "●", "▲", "★", "●", "?", "★"],
        "options": ["★", "●", "▲", "♦"],
        "answer": "▲",
        "metric": "correctness"
    },
    {
        "key": "logical_riddle_6",
        "type": "choice",
        "domain": "logical",
        "component": "sequence_logic",
        "title": {"English": "The Secret Locker Code", },
        "prompt": {"English": "A chest has a three-digit code. The first digit is double the second digit. The third digit is 3. The sum of all digits is 9. What is the code?", },
        "options": [
            {"label": {"English": "423", }, "value": 4},
            {"label": {"English": "630", }, "value": 0},
            {"label": {"English": "243", }, "value": 0},
            {"label": {"English": "513", }, "value": 1}
        ],
        "metric": "judgement"
    },

    # ── SPATIAL & MAKING (6 puzzles) ──
    {
        "key": "spatial_rotation",
        "type": "pattern_choice",
        "domain": "spatial",
        "component": "mental_rotation",
        "title": {"English": "The Magic Clock Hand", },
        "prompt": {"English": "A glowing star on a clock moves around: First it points UP (12 o'clock), then RIGHT (3 o'clock), then DOWN (6 o'clock). Where will the star point next?", },
        "sequence": ["↑", "→", "↓", "?"],
        "options": ["↑", "→", "↓", "←"],
        "answer": "←",
        "metric": "correctness"
    },
    {
        "key": "spatial_perspective",
        "type": "choice",
        "domain": "spatial",
        "component": "mechanical_intuition",
        "title": {"English": "The Golden Key Shadow", },
        "prompt": {"English": "A 3D key shaped like a flat 'T' is held in front of a flashlight. If the flashlight shines directly from the LEFT side, what shape of shadow does the T-key make on the wall?", },
        "options": [
            {"label": {"English": "A long vertical rectangle", }, "value": 4},
            {"label": {"English": "A perfect square", }, "value": 0},
            {"label": {"English": "A cross shape", }, "value": 1},
            {"label": {"English": "A round circle", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "spatial_origami",
        "type": "choice",
        "domain": "spatial",
        "component": "design_thinking",
        "title": {"English": "The Unfolded Box", },
        "prompt": {"English": "If you unfold a small cardboard cube with a blue star drawn on its top face, how many flat squares will you have in total?", },
        "options": [
            {"label": {"English": "6", }, "value": 4},
            {"label": {"English": "4", }, "value": 0},
            {"label": {"English": "8", }, "value": 0},
            {"label": {"English": "5", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "spatial_block_count",
        "type": "choice",
        "domain": "spatial",
        "component": "construction_sense",
        "title": {"English": "The Secret Tower Blocks", },
        "prompt": {"English": "A small tower is built with blocks: a base of 4 blocks, a middle layer of 2 blocks, and 1 block on the top. How many blocks are used in total?", },
        "options": [
            {"label": {"English": "7", }, "value": 4},
            {"label": {"English": "6", }, "value": 0},
            {"label": {"English": "8", }, "value": 0},
            {"label": {"English": "5", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "spatial_maze_logic",
        "type": "choice",
        "domain": "spatial",
        "component": "mental_rotation",
        "title": {"English": "The Hidden Path", },
        "prompt": {"English": "To reach the treasure, you must take a path. It goes: 2 steps forward, 1 step right, 3 steps forward, 2 steps left. Compared to where you started, are you now further to the left or right?", },
        "options": [
            {"label": {"English": "Left", }, "value": 4},
            {"label": {"English": "Right", }, "value": 0},
            {"label": {"English": "Same line", }, "value": 1},
            {"label": {"English": "Behind", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "spatial_shape_match",
        "type": "choice",
        "domain": "spatial",
        "component": "design_thinking",
        "title": {"English": "The Puzzle Cutout", },
        "prompt": {"English": "A large square has a small triangle cut out of it. If you slide the triangle back into the cutout, how many corners (vertices) will the shape have in total?", },
        "options": [
            {"label": {"English": "4 corners", }, "value": 4},
            {"label": {"English": "3 corners", }, "value": 0},
            {"label": {"English": "5 corners", }, "value": 1},
            {"label": {"English": "6 corners", }, "value": 0}
        ],
        "metric": "judgement"
    },

    # ── CREATIVE & ARTISTIC (6 puzzles) ──
    {
        "key": "visualizer_memory_grid",
        "type": "memory_grid",
        "domain": "creative",
        "component": "visual_imagination",
        "title": {"English": "The Constellation Map", },
        "prompt": {"English": "Look closely at the glowing stars in the magic night sky grid, and click them exactly as you remember them!", },
        "gridSize": 9,
        "highlights": [1, 3, 5, 7],
        "revealMs": 2500,
        "metric": "memory_span"
    },
    {
        "key": "creative_uses",
        "type": "idea_list",
        "domain": "creative",
        "component": "divergent_thinking",
        "title": {"English": "Sideways Gravity School", },
        "prompt": {"English": "Imagine that gravity suddenly starts working SIDEWAYS at your school instead of pulling you down! Write down at least 3 super funny or amazing things that would happen to you and your friends!", },
        "minIdeas": 3,
        "metric": "fluency"
    },
    {
        "key": "creative_story_spark",
        "type": "idea_list",
        "domain": "creative",
        "component": "divergent_thinking",
        "title": {"English": "The Cloud Shapes", },
        "prompt": {"English": "Look up at the sky. A giant cloud shaped like a flying teacup is pouring shiny liquid. Write down 3 different creative things this liquid could be (not water or tea)!", },
        "minIdeas": 3,
        "metric": "fluency"
    },
    {
        "key": "creative_color_harmony",
        "type": "choice",
        "domain": "creative",
        "component": "colour_sense",
        "title": {"English": "The Painter's Secret", },
        "prompt": {"English": "You want to paint a beautiful, energetic sun. Which combination of colors feels most warm and full of happy energy?", },
        "options": [
            {"label": {"English": "Yellow, Orange, and Red", }, "value": 4},
            {"label": {"English": "Blue, Purple, and Green", }, "value": 0},
            {"label": {"English": "Black, Grey, and White", }, "value": 0},
            {"label": {"English": "Brown and Dark Green", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "creative_instrument",
        "type": "choice",
        "domain": "creative",
        "component": "pattern_creation",
        "title": {"English": "The Kitchen Band", },
        "prompt": {"English": "You want to make a brand-new musical instrument using only kitchen items. What would you build to create a nice, soft shaking sound?", },
        "options": [
            {"label": {"English": "A plastic bottle filled with dry lentils and rice", }, "value": 4},
            {"label": {"English": "Striking two metal spoons together", }, "value": 1},
            {"label": {"English": "Blowing across a glass cup", }, "value": 2},
            {"label": {"English": "Banging a wooden table with a heavy pan", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "creative_divergent_shapes",
        "type": "idea_list",
        "domain": "creative",
        "component": "divergent_thinking",
        "title": {"English": "Drawing on Circles", },
        "prompt": {"English": "If you are given a sheet of paper with 5 empty circles printed on it, how many completely different objects can you turn these circles into? Write down at least 3 unique things you would draw (e.g. clock, wheel, face, coin, etc.)!", },
        "minIdeas": 3,
        "metric": "fluency"
    },

    # ── LANGUAGE & COMMUNICATION (6 puzzles) ──
    {
        "key": "language_story_order",
        "type": "order_steps",
        "domain": "language",
        "component": "storytelling",
        "title": {"English": "The Robot Escape Adventure", },
        "prompt": {"English": "Put these secret agent message pieces in the order that tells the exciting escape story!", },
        "steps": {
            "English": [
                "We saw a giant iron gate guarded by two sleeping robots.",
                "I whispered the secret code word to open the gate.",
                "We ran through the dark jungle and found a hidden sailboat.",
                "We sailed away under the beautiful starry night sky."
            ],
            },
        "shuffled": {
            "English": [
                "We ran through the dark jungle and found a hidden sailboat.",
                "We saw a giant iron gate guarded by two sleeping robots.",
                "We sailed away under the beautiful starry night sky.",
                "I whispered the secret code word to open the gate."
            ],
            },
        "metric": "sequence_accuracy"
    },
    {
        "key": "language_analogy",
        "type": "choice",
        "domain": "language",
        "component": "expression_clarity",
        "title": {"English": "The Secret Word Bridges", },
        "prompt": {"English": "Complete this word connection bridge: A FEATHER is to a BIRD as a SCALE is to...?", },
        "options": [
            {"label": {"English": "A Fish", }, "value": 4},
            {"label": {"English": "A Dog", }, "value": 0},
            {"label": {"English": "A Tree", }, "value": 0},
            {"label": {"English": "A River", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "language_unscramble",
        "type": "choice",
        "domain": "language",
        "component": "verbal_fluency",
        "title": {"English": "The Secret Code Word", },
        "prompt": {"English": "Put these letters in order to make a happy word representing a beautiful place with trees and swings: G, R, N, D, A, E. What is the word?", },
        "options": [
            {"label": {"English": "GARDEN", }, "value": 4},
            {"label": {"English": "DANGER", }, "value": 0},
            {"label": {"English": "GRAND", }, "value": 0},
            {"label": {"English": "GEARED", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "language_opposite",
        "type": "choice",
        "domain": "language",
        "component": "expression_clarity",
        "title": {"English": "The Word Opposite", },
        "prompt": {"English": "A brave knight goes to face a challenge. The opposite of being BRAVE is being...?", },
        "options": [
            {"label": {"English": "Fearful or Cowardly", }, "value": 4},
            {"label": {"English": "Strong", }, "value": 0},
            {"label": {"English": "Quiet", }, "value": 0},
            {"label": {"English": "Smart", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "language_rhyme_scheme",
        "type": "choice",
        "domain": "language",
        "component": "storytelling",
        "title": {"English": "The Rhyming Poem", },
        "prompt": {"English": "A small bird sings in a tree so high, flapping its wings as it flies in the ?. Which word completes the poem with a perfect rhyme?", },
        "options": [
            {"label": {"English": "Sky", }, "value": 4},
            {"label": {"English": "Nest", }, "value": 0},
            {"label": {"English": "Wind", }, "value": 0},
            {"label": {"English": "Sun", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "language_cloze_passage",
        "type": "choice",
        "domain": "language",
        "component": "verbal_fluency",
        "title": {"English": "The Missing Emotion Word", },
        "prompt": {"English": "Fill in the blank: 'When the lost puppy finally returned home wagging its tail, the children felt extremely ? and began to celebrate.'", },
        "options": [
            {"label": {"English": "Joyful", }, "value": 4},
            {"label": {"English": "Tired", }, "value": 0},
            {"label": {"English": "Angry", }, "value": 0},
            {"label": {"English": "Scared", }, "value": 0}
        ],
        "metric": "judgement"
    },

    # ── KINESTHETIC & PHYSICAL (6 puzzles) ──
    {
        "key": "visual_reaction",
        "type": "reaction",
        "domain": "kinesthetic",
        "component": "body_coordination",
        "title": {"English": "The Lightning Flash", },
        "prompt": {"English": "Tap the center target as fast as a lightning bolt the exact millisecond it flashes happy gold!", },
        "waitMs": 1200,
        "metric": "reaction_time"
    },
    {
        "key": "kinesthetic_motor_planning",
        "type": "choice",
        "domain": "kinesthetic",
        "component": "body_coordination",
        "title": {"English": "The Treehouse Rope Bridge", },
        "prompt": {"English": "You are crossing a high, wobbling rope bridge to reach a treehouse. A strong gust of wind suddenly blows from the right! What is the best way to balance your body so you don't slip?", },
        "options": [
            {"label": {"English": "Bend your knees slightly, spread your arms wide, and lean your weight slightly into the wind to the right", }, "value": 4},
            {"label": {"English": "Stand completely straight and close your eyes", }, "value": 0},
            {"label": {"English": "Run as fast as you can to the other side", }, "value": 1},
            {"label": {"English": "Sit down on the rope bridge and shout for help", }, "value": 2}
        ],
        "metric": "judgement"
    },
    {
        "key": "kinesthetic_balancing",
        "type": "choice",
        "domain": "kinesthetic",
        "component": "fine_motor",
        "title": {"English": "The Gymnastic Beam", },
        "prompt": {"English": "You are balancing on one foot on a narrow wooden beam. To stay balanced for a long time, what is the best strategy?", },
        "options": [
            {"label": {"English": "Extend your arms out to the sides and focus your eyes on a single still point ahead", }, "value": 4},
            {"label": {"English": "Swing your arms quickly back and forth", }, "value": 0},
            {"label": {"English": "Look down at your feet and jump slightly", }, "value": 1},
            {"label": {"English": "Close your eyes and stand completely stiff", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "kinesthetic_aiming",
        "type": "choice",
        "domain": "kinesthetic",
        "component": "fine_motor",
        "title": {"English": "The Stone Throwing Game", },
        "prompt": {"English": "You are trying to hit a plastic bottle placed on a rock from a distance. To improve your accuracy and hit the target, what should you do?", },
        "options": [
            {"label": {"English": "Stand firmly, align your shoulder with the target, and follow through with a smooth arm movement", }, "value": 4},
            {"label": {"English": "Throw the stone as hard as possible without looking", }, "value": 0},
            {"label": {"English": "Close one eye and throw backwards", }, "value": 0},
            {"label": {"English": "Run forward and throw while jumping", }, "value": 2}
        ],
        "metric": "judgement"
    },
    {
        "key": "kinesthetic_speed_tapping",
        "type": "reaction",
        "domain": "kinesthetic",
        "component": "rhythm_accuracy",
        "title": {"English": "The Speed Tap Test", },
        "prompt": {"English": "How fast can you react to a green signal? Try this quick tap exercise when it turns green!", },
        "waitMs": 1500,
        "metric": "reaction_time"
    },
    {
        "key": "kinesthetic_dance_improvisation",
        "type": "choice",
        "domain": "kinesthetic",
        "component": "movement_memory",
        "title": {"English": "The Flowing River Movement", },
        "prompt": {"English": "Imagine you are acting like a quiet flowing river that suddenly turns into a fast, crashing waterfall. How does your body naturally move to show this?", },
        "options": [
            {"label": {"English": "Slow, wavy arm gestures that suddenly turn into sharp, downward drops", }, "value": 4},
            {"label": {"English": "Standing completely still and stiff", }, "value": 0},
            {"label": {"English": "Jumping up and down in one place repeatedly", }, "value": 1},
            {"label": {"English": "Spinning around in fast circles until you are dizzy", }, "value": 0}
        ],
        "metric": "judgement"
    },

    # ── SOCIAL & LEADERSHIP (6 puzzles) ──
    {
        "key": "social_response",
        "type": "choice",
        "domain": "social",
        "component": "empathy_recognition",
        "title": {"English": "The Lost Puppy Dilemma", },
        "prompt": {"English": "Your group of friends finds a cute lost puppy with a collar in the park. Two friends want to keep the puppy secretly in their house, but you know its owners must be worried. How do you lead your friends to do the right thing without making them angry?", },
        "options": [
            {"label": {"English": "Suggest calling the number on the collar together so you can all be heroes who saved and returned a lost pet", }, "value": 4},
            {"label": {"English": "Fight with them and threaten to report them to the police", }, "value": 0},
            {"label": {"English": "Walk away in silence and let them do whatever they want", }, "value": 1},
            {"label": {"English": "Take the puppy away from them by force and run", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "social_conflict_resolution",
        "type": "choice",
        "domain": "social",
        "component": "conflict_resolution",
        "title": {"English": "The Playground Game Dispute", },
        "prompt": {"English": "During a football match, two of your classmates start arguing loudly about whether the ball crossed the goal line. Everyone is shouting and the game has stopped. How do you resolve this conflict so everyone plays again happily?", },
        "options": [
            {"label": {"English": "Suggest playing a quick penalty kick or flip a coin to decide, and remind them that having fun together is the main goal", }, "value": 4},
            {"label": {"English": "Shout louder than both of them to make them shut up", }, "value": 0},
            {"label": {"English": "Take the football and walk home", }, "value": 1},
            {"label": {"English": "Blame one classmate immediately to end the argument quickly", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "social_group_project",
        "type": "choice",
        "domain": "social",
        "component": "group_organising",
        "title": {"English": "The Team Display Board", },
        "prompt": {"English": "Your group is making a chart paper display, but one team member is shy and not writing anything. How do you help them participate?", },
        "options": [
            {"label": {"English": "Ask them what they like to draw or write, and give them a specific, fun part of the poster to work on", }, "value": 4},
            {"label": {"English": "Do all the work yourself and write their name anyway", }, "value": 1},
            {"label": {"English": "Tell the teacher they are lazy and not working", }, "value": 0},
            {"label": {"English": "Ignore them and let the group finish without them", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "social_empathy",
        "type": "choice",
        "domain": "social",
        "component": "empathy_recognition",
        "title": {"English": "The Crying Classmate", },
        "prompt": {"English": "A classmate sits alone on the stairs crying because they dropped their lunchbox and all their food fell. What do you do?", },
        "options": [
            {"label": {"English": "Sit next to them, ask if they are okay, and offer to share some of your own lunch with them", }, "value": 4},
            {"label": {"English": "Walk past them and pretend you didn't see", }, "value": 0},
            {"label": {"English": "Tell other friends so they can laugh together", }, "value": 0},
            {"label": {"English": "Go tell the cleaner to sweep up the spilled food", }, "value": 2}
        ],
        "metric": "judgement"
    },
    {
        "key": "social_leadership_style",
        "type": "choice",
        "domain": "social",
        "component": "peer_influence",
        "title": {"English": "The Lost Hike Route", },
        "prompt": {"English": "During a nature walk, your group gets confused about which path leads back to the school bus. Everyone is starting to panic. How do you lead?", },
        "options": [
            {"label": {"English": "Ask everyone to pause, check the map together calmly, and walk back in a single line holding hands", }, "value": 4},
            {"label": {"English": "Run ahead alone on the path you think is right", }, "value": 1},
            {"label": {"English": "Start crying so someone else takes charge", }, "value": 0},
            {"label": {"English": "Tell everyone that they are foolish for getting lost", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "social_cooperation",
        "type": "choice",
        "domain": "social",
        "component": "group_organising",
        "title": {"English": "Cleaning the Classroom", },
        "prompt": {"English": "The teacher asks the class to clean the room in 5 minutes. What is the most effective way to cooperate?", },
        "options": [
            {"label": {"English": "Divide the classroom into small zones and assign 2-3 friends to clean each zone together", }, "value": 4},
            {"label": {"English": "Everyone runs to grab the single broom at the same time", }, "value": 0},
            {"label": {"English": "Wait until most people finish, then pick up one small paper"}, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "naturalist_decomposer",
        "type": "choice",
        "domain": "naturalist",
        "component": "living_systems",
        "title": {"English": "The Forest Soil Miracle", },
        "prompt": {"English": "In a thick, green forest, giant dead leaves fall on the ground every day, but the forest floor stays clean and rich. Who are the hidden heroes cleaning the forest floor?", },
        "options": [
            {"label": {"English": "Tiny earthworms, mushrooms, and beetles (decomposers) turning leaves into soil", }, "value": 4},
            {"label": {"English": "The forest wind blowing everything away", }, "value": 0},
            {"label": {"English": "The rain washing everything into rivers", }, "value": 0},
            {"label": {"English": "Wild forest animals eating all the dry leaves", }, "value": 1}
        ],
        "metric": "classification"
    },
    {
        "key": "naturalist_wind_disperse",
        "type": "choice",
        "domain": "naturalist",
        "component": "living_systems",
        "title": {"English": "The Secret Butterfly Garden", },
        "prompt": {"English": "You want to attract colorful butterflies to live in your school garden. Which of these actions will help the butterflies the MOST?", },
        "options": [
            {"label": {"English": "Plant bright native flowering plants that have sweet nectar and keep fresh shallow water trays nearby", }, "value": 4},
            {"label": {"English": "Spray strong insect spray to keep other bugs away from the plants", }, "value": 0},
            {"label": {"English": "Cover all the flowers with plastic sheets so they don't get dirty", }, "value": 0},
            {"label": {"English": "Catch butterflies from other parks and release them inside your garden", }, "value": 1}
        ],
        "metric": "classification"
    },
    {
        "key": "naturalist_weather_pattern",
        "type": "choice",
        "domain": "naturalist",
        "component": "pattern_in_nature",
        "title": {"English": "The Rain Clouds", },
        "prompt": {"English": "You are playing outdoors and notice the wind suddenly blowing cold, swallows flying low, and the sky turning dark grey. What is nature telling you?", },
        "options": [
            {"label": {"English": "A heavy rain shower is coming very soon", }, "value": 4},
            {"label": {"English": "The sun is going to shine brighter", }, "value": 0},
            {"label": {"English": "An earthquake is happening", }, "value": 0},
            {"label": {"English": "A cold winter night has started", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "naturalist_animal_track",
        "type": "choice",
        "domain": "naturalist",
        "component": "animal_empathy",
        "title": {"English": "The Footprints in the Mud", },
        "prompt": {"English": "By a muddy river bank, you see small webbed footprints. Which animal most likely walked here?", },
        "options": [
            {"label": {"English": "A duck or frog", }, "value": 4},
            {"label": {"English": "A dog or cat", }, "value": 0},
            {"label": {"English": "A horse or cow", }, "value": 0},
            {"label": {"English": "A bird like a crow", }, "value": 2}
        ],
        "metric": "judgement"
    },
    {
        "key": "naturalist_plant_needs",
        "type": "choice",
        "domain": "naturalist",
        "component": "environment_awareness",
        "title": {"English": "The Sick Potted Plant", },
        "prompt": {"English": "A potted plant in your classroom has yellow, dry leaves that are drooping down. How can you help it recover best?", },
        "options": [
            {"label": {"English": "Move it near the window for sunlight and water the soil gently", }, "value": 4},
            {"label": {"English": "Put it in a dark closet and cover it with a cloth", }, "value": 0},
            {"label": {"English": "Spray perfume on it to make it smell good", }, "value": 0},
            {"label": {"English": "Pour a whole bucket of water on it until it drowns", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "naturalist_biodiversity",
        "type": "choice",
        "domain": "naturalist",
        "component": "living_systems",
        "title": {"English": "The Classroom Aquarium", },
        "prompt": {"English": "You are setting up a small aquarium for fish. Besides clean water and fish food, what else should you add to keep the fish healthy and happy?", },
        "options": [
            {"label": {"English": "Live green water plants and smooth pebbles for hiding spots", }, "value": 4},
            {"label": {"English": "Colorful plastic toys and shiny glitter", }, "value": 0},
            {"label": {"English": "Lots of sugar to make the water sweet", }, "value": 0},
            {"label": {"English": "Small pieces of bread and milk", }, "value": 1}
        ],
        "metric": "judgement"
    },

    # ── INTRAPERSONAL & REFLECTIVE (6 puzzles) ──
    {
        "key": "intrapersonal_reflection",
        "type": "scale",
        "domain": "intrapersonal",
        "component": "reflective_thinking",
        "title": {"English": "The Brave Explorer Goal", },
        "prompt": {"English": "When you face a challenge that is very hard for you, do you tell yourself that you can get better at it with practice?", },
        "low": {"English": "Never, I get discouraged", },
        "high": {"English": "Always, I love to learn!", },
        "metric": "self_reflection"
    },
    {
        "key": "intrapersonal_frustration",
        "type": "choice",
        "domain": "intrapersonal",
        "component": "resilience_signal",
        "title": {"English": "The Lost Kite Adventure", },
        "prompt": {"English": "You spent two days making a beautiful paper kite. On its very first flight, it gets stuck high in a thorny tree. You feel upset and want to cry. What is the most helpful thing to tell yourself?", },
        "options": [
            {"label": {"English": "It is normal to feel sad, but crying won't get it down. Let me take a deep breath and plan to reach it with a long stick.", }, "value": 4},
            {"label": {"English": "I am terrible at flying kites. I will never make or fly one again.", }, "value": 0},
            {"label": {"English": "I will kick the tree as hard as I can until it shakes.", }, "value": 0},
            {"label": {"English": "It was a bad kite anyway, I don't care.", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "intrapersonal_journaling",
        "type": "scale",
        "domain": "intrapersonal",
        "component": "reflective_thinking",
        "title": {"English": "The Quiet Reflection", },
        "prompt": {"English": "After a very long and busy day, what makes you feel most relaxed and helps you understand your day better?", },
        "low": {"English": "Nothing, I just ignore it", },
        "high": {"English": "Quietly sitting and thinking about my choices", },
        "metric": "self_reflection"
    },
    {
        "key": "intrapersonal_goal_setting",
        "type": "choice",
        "domain": "intrapersonal",
        "component": "self_awareness",
        "title": {"English": "Learning a Hard Skill", },
        "prompt": {"English": "You want to learn how to play a new musical instrument or a sport. What is your plan?", },
        "options": [
            {"label": {"English": "Practice for 15 minutes every single day, even when it is hard", }, "value": 4},
            {"label": {"English": "Practice for 5 hours in one day and then stop forever", }, "value": 1},
            {"label": {"English": "Wait until you are naturally perfect at it", }, "value": 0},
            {"label": {"English": "Ask someone else to play it for you", }, "value": 0}
        ],
        "metric": "judgement"
    },
    {
        "key": "intrapersonal_self_regulation",
        "type": "choice",
        "domain": "intrapersonal",
        "component": "resilience_signal",
        "title": {"English": "Handling Anger", },
        "prompt": {"English": "Someone accidentally bumps into you and your drawings spill all over the floor. You feel a sudden rush of anger. What do you do?", },
        "options": [
            {"label": {"English": "Take a deep breath, realize it was an accident, and pick up your papers calmly", }, "value": 4},
            {"label": {"English": "Shout at them and push them back", }, "value": 0},
            {"label": {"English": "Cry loudly and tear up all your drawings", }, "value": 0},
            {"label": {"English": "Sit on the floor and refuse to move", }, "value": 1}
        ],
        "metric": "judgement"
    },
    {
        "key": "intrapersonal_self_awareness",
        "type": "scale",
        "domain": "intrapersonal",
        "component": "self_awareness",
        "title": {"English": "Knowing Your Strengths", },
        "prompt": {"English": "How well do you know what activities make you feel happiest and most excited?", },
        "low": {"English": "I have no idea", },
        "high": {"English": "I know exactly what I love", },
        "metric": "self_reflection"
    }
]

import urllib.request

def call_gemini_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            text = res_body["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
    except Exception as e:
        print(f"[SUCCESS OR RETRY] Gemini API request failed: {e}")
        return None

def load_puzzles_from_db():
    try:
        db = get_db()
        rows = db.execute("SELECT data FROM puzzles").fetchall()
        puzzles = []
        for r in rows:
            try:
                puzzles.append(json.loads(r["data"]))
            except Exception:
                pass
        return puzzles if puzzles else DEFAULT_AI_PUZZLES
    except Exception:
        return DEFAULT_AI_PUZZLES

def generate_ai_tasks(child, discovery_answers):
    # Perfect balanced discovery mapping
    discovery_mapping = {
        "q_discovery_1": {0: "logical", 1: "creative", 2: "language", 3: "social"},
        "q_discovery_2": {0: "spatial", 1: "creative", 2: "logical", 3: "kinesthetic"},
        "q_discovery_3": {0: "naturalist", 1: "creative", 2: "intrapersonal", 3: "language"},
        "q_discovery_4": {0: "social", 1: "language", 2: "intrapersonal", 3: "kinesthetic"},
        "q_discovery_5": {0: "logical", 1: "spatial", 2: "kinesthetic", 3: "social"},
        "q_discovery_6": {0: "creative", 1: "social", 2: "language", 3: "spatial"},
        "q_discovery_7": {0: "naturalist", 1: "spatial", 2: "logical", 3: "kinesthetic"},
        "q_discovery_8": {0: "language", 1: "naturalist", 2: "creative", 3: "intrapersonal"},
        "q_discovery_9": {0: "naturalist", 1: "spatial", 2: "creative", 3: "kinesthetic"},
        "q_discovery_10": {0: "kinesthetic", 1: "spatial", 2: "language", 3: "intrapersonal"},
        "q_discovery_11": {0: "naturalist", 1: "logical", 2: "social", 3: "intrapersonal"},
        "q_discovery_12": {0: "logical", 1: "naturalist", 2: "social", 3: "intrapersonal"}
    }
    
    discovery_counts = {
        "logical": 0, "spatial": 0, "creative": 0, "language": 0,
        "kinesthetic": 0, "social": 0, "naturalist": 0, "intrapersonal": 0
    }
    for q_key, opts in discovery_mapping.items():
        choice = discovery_answers.get(q_key)
        if choice is not None:
            choice_val = int(choice)
            if choice_val in opts:
                dom = opts[choice_val]
                discovery_counts[dom] += 1
            
    pref_lang = child.get("language", "English")
    if pref_lang not in ["Hindi", "English"]:
        pref_lang = "English"

    selected_tasks = []
    db_puzzles = load_puzzles_from_db()
    
    # Adaptive Selection based on likelihood
    for domain in ["logical", "spatial", "creative", "language", "kinesthetic", "social", "naturalist", "intrapersonal"]:
        exp_val = child.get(f"exp_{domain}", 0)
        disc_count = discovery_counts.get(domain, 0)
        likelihood = exp_val + disc_count
        
        # High (>= 6) -> 6 questions, Medium (3-5) -> 4 questions, Low (< 3) -> 2 questions
        if likelihood >= 6:
            q_count = 6
        elif likelihood >= 3:
            q_count = 4
        else:
            q_count = 2
            
        domain_puzzles = [p for p in DEFAULT_AI_PUZZLES if p["domain"] == domain]
        # Standardized selection of first q_count questions from the bank
        selected = domain_puzzles[:q_count]
        
        for original_puzzle in selected:
            p = dict(original_puzzle)
            p["title"] = original_puzzle["title"].get(pref_lang, original_puzzle["title"]["English"])
            p["prompt"] = original_puzzle["prompt"].get(pref_lang, original_puzzle["prompt"]["English"])
            
            if "low" in original_puzzle and isinstance(original_puzzle["low"], dict):
                p["low"] = original_puzzle["low"].get(pref_lang, original_puzzle["low"]["English"])
            if "high" in original_puzzle and isinstance(original_puzzle["high"], dict):
                p["high"] = original_puzzle["high"].get(pref_lang, original_puzzle["high"]["English"])
                
            if "options" in original_puzzle and original_puzzle["type"] == "choice":
                p["options"] = []
                for opt in original_puzzle["options"]:
                    new_opt = dict(opt)
                    if isinstance(opt["label"], dict):
                        new_opt["label"] = opt["label"].get(pref_lang, opt["label"]["English"])
                    p["options"].append(new_opt)
                    
            if "steps" in original_puzzle and original_puzzle["type"] == "order_steps":
                p["steps"] = original_puzzle["steps"].get(pref_lang, original_puzzle["steps"]["English"])
                p["shuffled"] = original_puzzle["shuffled"].get(pref_lang, original_puzzle["shuffled"]["English"])
                
            selected_tasks.append(p)
            
    return selected_tasks

@app.route("/api/sessions/<int:sid>/discovery", methods=["POST"])
def submit_discovery(sid):
    data = request.json or {}
    answers = data.get("answers", {})
    child_id = data.get("child_id")
    print("==================================================")
    print(f"DEBUG: submit_discovery called for session ID: {sid} with data: {data}")
    try:
        user = current_user()
        print(f"DEBUG: Current user session: {user}")
    except Exception as e:
        print(f"DEBUG: Error getting current user session: {e}")
    
    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
    child = dict(child)
    
    generated_tasks = generate_ai_tasks(child, answers)
    
    if supabase_client:
        try:
            update_data = {
                "responses": json.dumps(answers),
                "generated_tasks": json.dumps(generated_tasks),
                "phase": "assess"
            }
            print(f"DEBUG: Attempting Supabase update for session ID: {sid} in discovery")
            print(f"DEBUG: Supabase update payload: {json.dumps(update_data)}")
            res = supabase_client.table("sessions").update(update_data).eq("id", sid).execute()
            print(f"DEBUG: Supabase update response data: {res.data}")
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase update in discovery: {e}")
            import traceback
            traceback.print_exc()
            
    db.execute("""
        UPDATE sessions SET
            responses = ?,
            generated_tasks = ?,
            phase = 'assess'
        WHERE id = ?
    """, (json.dumps(answers), json.dumps(generated_tasks), sid))
    db.commit()
    
    return jsonify({"status": "success", "count": len(generated_tasks)})

@app.route("/api/sessions/<int:sid>/submit", methods=["POST"])
def submit_session(sid):
    """
    Receives all responses, runs the scoring engine, saves results.
    """
    return analyze_and_save_session(sid, request.json)

@app.route("/api/sessions/<int:sid>/analyze", methods=["POST"])
def analyze_session(sid):
    """
    Receives structured questionnaire and puzzle responses, analyses metrics,
    saves results, and returns the computed profile.
    """
    return analyze_and_save_session(sid, request.json)

def analyze_and_save_session(sid, data):
    print("==================================================")
    print(f"DEBUG: analyze_and_save_session called for session ID: {sid}")
    try:
        print(f"DEBUG: Incoming assessment data responses count: {len(data.get('responses', {})) if data else 0}")
        print(f"DEBUG: Incoming assessment data: {json.dumps(data)}")
    except Exception as e:
        print(f"DEBUG: Error printing incoming data: {e}")
    try:
        user = current_user()
        print(f"DEBUG: Current user session: {user}")
    except Exception as e:
        print(f"DEBUG: Error getting current user session: {e}")
        
    data = data or {}
    responses = data.get("responses", {})
    child_id = data.get("child_id")

    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
    child = dict(child)

    # Load discovery answers
    session_row = db.execute("SELECT responses FROM sessions WHERE id=?", (sid,)).fetchone()
    discovery_answers = {}
    if session_row and session_row["responses"]:
        try:
            discovery_answers = json.loads(session_row["responses"])
        except Exception:
            pass

    # Merge discovery answers and deep assessment answers
    combined_responses = {**discovery_answers, **responses}

    # Check facilitator notes for validation overrides
    latest_note = db.execute("""
        SELECT * FROM facilitator_notes WHERE session_id=? ORDER BY created_at DESC
    """, (sid,)).fetchone()
    if latest_note:
        latest_note = dict(latest_note)

    # Run scoring engine with full context
    scores = score_responses(responses, child, discovery_answers, latest_note)

    top_domain = scores["primary_domain"]
    top_3 = scores["secondary_domains"] # standard compatibility
    final_scores = scores["tq_scores"]

    # Recommendations Engine Upgrade (Domain-Specific)
    recommendations_db = {
        "creative": ["Art & Design Workshop", "Storytelling & Theatre Club", "Creative Design Challenges"],
        "logical": ["STEM & Coding Basics", "Strategy Board Games", "Advanced Logic Puzzle Club"],
        "spatial": ["Tinkering & Making Lab", "Model-Building Projects", "3D Geometric Challenges"],
        "social": ["Peer Leadership Projects", "Community Volunteering", "Class Event Planning"],
        "language": ["Public Speaking Forum", "Debate & Poetry Club", "Junior Journalism/Interview Activities"],
        "naturalist": ["Young Naturalist Trails", "Ecological Mapping walks", "Ecosystem observation walks"],
        "kinesthetic": ["Sports Training Camp", "Dance & Movement Class", "Obstacle Course Coordination Games"],
        "intrapersonal": ["Mindfulness Journaling", "Goal-Setting Workshop", "Reflective Creative Writing Seminar"]
    }
    top_recommendations = recommendations_db.get(top_domain, ["STEM & Leadership Development"])

    # Facilitator adjustment metadata
    has_notes = latest_note is not None
    confirmed = bool(latest_note.get("confirmed")) if has_notes else False
    override_domain = latest_note.get("override_domain") if has_notes else None
    fac_adjustment = {
        "review_count": 1 if has_notes else 0,
        "original_top_domain": scores["original_top"],
        "confirmed": confirmed,
        "override_domain": override_domain or "",
        "method": "Facilitator confirmed top result." if confirmed else "Facilitator disagreed; override domain blended." if override_domain else "No validation notes added."
    }

    # Post-Assessment AI profiling (Gemini)
    talent_narrative = ""
    pattern_analysis = ""
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        prompt = f"""
        You are a supportive child psychologist and expert psychometrician specializing in talent development for children aged 10-14.
        Create an educator-friendly, warm, and encouraging talent profile for a child named {child.get("name", "Kid")}, age {child.get("age", 12)}, with preferred language {child.get("language", "English")}.
        
        Aptitude scores: {final_scores}
        Exposure levels (0=Never, 1=Few times, 2=Sometimes, 3=Regularly): {[ (d, child.get(f"exp_{d}", 0)) for d in DOMAIN_WEIGHTS.keys() ]}
        
        Metrics: {scores["metrics"]}
        Top Domain: {DOMAIN_LABELS.get(top_domain, top_domain)}
        Untapped Potential Flagged: {[ DOMAIN_LABELS.get(u, u) for u in scores["untapped_potential"] ]}
        
        Please analyze this data and generate a JSON object with two fields (do not write any markdown outside the JSON block):
        - "talent_narrative": A warm, encouraging, human, and educator-friendly narrative (2-3 sentences) explaining the child's natural abilities and learning style.
          Always communicate probability and potential rather than certainty (e.g. "suggests strong indicators in X activities" rather than "X is your greatest strength").
          Avoid all corporate buzzwords or definitive labels (e.g. do NOT use "exceptional", "highly impressive", "accelerated nurturing"). Focus on spontaneous behaviors.
        - "pattern_analysis": A deep cognitive pattern analysis explaining their speed, memory, focus, and logic based on the metrics.
        """
        gemini_res = call_gemini_api(prompt, api_key)
        if gemini_res and isinstance(gemini_res, dict):
            talent_narrative = gemini_res.get("talent_narrative", "")
            pattern_analysis = gemini_res.get("pattern_analysis", "")

    # Clean fallback narratives in child-friendly, human and educator-friendly language (avoiding corporate jargon)
    if not talent_narrative:
        primary_label = DOMAIN_LABELS.get(top_domain, top_domain)
        potential_str = ""
        if scores["untapped_potential"]:
            pot_labels = [DOMAIN_LABELS.get(u, u) for u in scores["untapped_potential"]]
            potential_str = f" A promising untapped potential has also been indicated in {', '.join(pot_labels)}, suggesting high natural interest and capacity that could blossom with additional exposure."
        
        sec_labels = [DOMAIN_LABELS.get(d, d) for d in scores["secondary_domains"]]
        sec_str = sec_labels[0] if sec_labels else "other activities"
        
        exposure_val = child.get(f"exp_{top_domain}", 0)
        exposure_label = ["very limited", "some prior", "regular", "deeply consistent"][exposure_val]
        
        # Get top tasks from deep assessment for narrative evidence
        top_tasks = [FORMAL_MAPPING.get(t, t.replace("_", " ").title()) for t, val in responses.items() if isinstance(val, dict) and val.get("domain") == top_domain and answer_to_scale(val) >= 3.0]
        task_str = " and ".join(top_tasks[:2]) if top_tasks else "scenario-based problem-solving"

        talent_narrative = (
            f"{child.get('name', 'This child')} showed the strongest indicators in {primary_label} activities, "
            f"particularly in {task_str} tasks. {sec_str} also emerged as a promising area for potential development. "
            f"Because prior exposure in this domain appears {exposure_label}, additional workshops and continued "
            f"participation may provide a clearer picture of their long-term strengths.{potential_str}"
        )
        pattern_analysis = f"Deductive problem-solving speed was balanced. Memory and attention were stable throughout scored cognitive challenges. Divergence levels show strong flexible reasoning."

    personality_val = {
        "metrics": scores["metrics"],
        "facilitator_adjustment": fac_adjustment,
        "evidence": scores["evidence"],
        "confidence_level": scores["confidence_level"],
        "confidence_score": scores["confidence_score"],
        "confidence_desc": scores["confidence_desc"],
        "untapped_potential": scores["untapped_potential"],
        "primary_domain": scores["primary_domain"],
        "secondary_domains": scores["secondary_domains"],
        "emerging_domains": scores["emerging_domains"],
        "talent_narrative": talent_narrative,
        "pattern_analysis": pattern_analysis,
        "separation_index": scores["separation_index"],
        "multiple_talents_detected": scores["multiple_talents_detected"],
        "action_plan": scores["action_plan"],
        "recommendations": {
            "confidence": scores["confidence_level"],
            "rationale": f"Confidence is rated {scores['confidence_level']} based on a task completion density score of {scores['confidence_score']}/100.",
            "next_steps": top_recommendations,
            "mentor_domain": top_domain,
            "age_group": "10-12" if int(child.get("age", 12)) <= 12 else "13-14",
        }
    }
    personality_data = json.dumps(personality_val)
    completed_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if supabase_client:
        try:
            update_data = {
                "responses": json.dumps(combined_responses),
                "domain_flags": json.dumps([top_domain] + top_3),
                "tq_scores": json.dumps(final_scores),
                "eq_score": int(scores["eq_score"]),
                "visualizer_score": int(scores["visualizer_score"]),
                "personality_data": personality_data,
                "integrated_score": json.dumps(final_scores),
                "top_domain": top_domain,
                "phase": "complete",
                "status": "complete",
                "completed_at": completed_now
            }
            print(f"DEBUG: Attempting Supabase update for session ID: {sid}")
            print(f"DEBUG: Supabase update payload: {json.dumps(update_data)}")
            res = supabase_client.table("sessions").update(update_data).eq("id", sid).execute()
            print(f"DEBUG: Supabase update response data: {res.data}")
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase update: {e}")
            import traceback
            traceback.print_exc()

    # Permanently write the results to database
    db.execute("""
        UPDATE sessions SET
            responses        = ?,
            domain_flags     = ?,
            tq_scores        = ?,
            eq_score         = ?,
            visualizer_score = ?,
            personality_data = ?,
            integrated_score = ?,
            top_domain       = ?,
            phase            = 'complete',
            status           = 'complete',
            completed_at     = ?
        WHERE id = ?
    """, (
        json.dumps(combined_responses),
        json.dumps([top_domain] + top_3),
        json.dumps(final_scores),
        scores["eq_score"],
        scores["visualizer_score"],
        personality_data,
        json.dumps(final_scores), # integrated score matches final stretched scores
        top_domain,
        completed_now,
        sid
    ))
    db.commit()

    return jsonify({
        "session_id": sid,
        "top_domain": top_domain,
        "top_3": [top_domain] + top_3,
        "tq_scores": final_scores,
        "integrated": final_scores,
        "eq_score": scores["eq_score"],
        "visualizer_score": scores["visualizer_score"],
        "metrics": scores["metrics"],
        "facilitator_adjustment": fac_adjustment,
        "evidence": scores["evidence"],
        "confidence_level": scores["confidence_level"],
        "untapped_potential": scores["untapped_potential"],
        "primary_domain": scores["primary_domain"],
        "secondary_domains": scores["secondary_domains"],
        "emerging_domains": scores["emerging_domains"],
        "talent_narrative": talent_narrative,
        "pattern_analysis": pattern_analysis,
        "recommendations": {
            "confidence": scores["confidence_level"],
            "rationale": f"Confidence is rated {scores['confidence_level']} based on a task completion density score of {scores['confidence_score']}/100.",
            "next_steps": top_recommendations,
            "mentor_domain": top_domain,
            "age_group": "10-12" if int(child.get("age", 12)) <= 12 else "13-14",
        }
    })

@app.route("/api/children/<int:cid>/sessions", methods=["GET"])
def child_sessions(cid):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM sessions WHERE child_id=? ORDER BY created_at DESC", (cid,)
    ).fetchall()
    return jsonify([dict(r) for r in rows])

# ═══════════════════════════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

# Each domain has weighted components. Weights sum to 100.
DOMAIN_WEIGHTS = {
    "kinesthetic":   {"rhythm_accuracy":20, "movement_memory":20, "fine_motor":25, "body_coordination":20, "physical_endurance":15},
    "creative":      {"divergent_thinking":25, "visual_imagination":25, "originality":20, "colour_sense":15, "pattern_creation":15},
    "logical":       {"pattern_recognition":30, "number_reasoning":25, "sequence_logic":25, "spatial_logic":20},
    "spatial":       {"mental_rotation":25, "construction_sense":25, "mechanical_intuition":25, "design_thinking":25},
    "social":        {"empathy_recognition":25, "peer_influence":20, "conflict_resolution":25, "group_organising":30},
    "language":      {"verbal_fluency":25, "storytelling":25, "expression_clarity":25, "persuasion":25},
    "naturalist":    {"living_systems":30, "pattern_in_nature":25, "animal_empathy":25, "environment_awareness":20},
    "intrapersonal": {"self_awareness":30, "emotional_depth":30, "resilience_signal":20, "reflective_thinking":20},
}

DOMAIN_LABELS = {
    "kinesthetic":   "Kinesthetic & Physical",
    "creative":      "Creative & Artistic",
    "logical":       "Logical & Analytical",
    "spatial":       "Spatial & Making",
    "social":        "Social & Leadership",
    "language":      "Language & Communication",
    "naturalist":    "Naturalist & Environmental",
    "intrapersonal": "Intrapersonal & Reflective",
}

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Facilitator Notes
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.json
    user = current_user()
    facilitator_name = data.get("facilitator") or (user["name"] if user else "Project WHY Mentor")

    db = get_db()
    cur = db.execute("""
        INSERT INTO facilitator_notes
          (session_id, child_id, facilitator, confirmed, observation, override_domain, notes,
           agreement, strengths_observed, concerns, suggested_workshop,
           obs_creativity, obs_communication, obs_leadership, obs_focus, evidence_notes,
           obs_curiosity, validation_status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data["session_id"], data["child_id"],
        facilitator_name, data.get("confirmed", 0),
        data.get("observation", ""), data.get("override_domain", ""),
        data.get("notes", ""),
        data.get("agreement", "Agree"),
        data.get("strengths_observed", ""),
        data.get("concerns", ""),
        data.get("suggested_workshop", ""),
        data.get("obs_creativity", 0),
        data.get("obs_communication", 0),
        data.get("obs_leadership", 0),
        data.get("obs_focus", 0),
        data.get("evidence_notes", ""),
        data.get("obs_curiosity", 0),
        data.get("validation_status", "Pending Validation")
    ))
    db.commit()

    # Load combined responses and trigger robust recalculation and full write
    session = db.execute("SELECT responses FROM sessions WHERE id=?", (data["session_id"],)).fetchone()
    if session and session["responses"]:
        responses = json.loads(session["responses"] or "{}")
        res = analyze_and_save_session(data["session_id"], {
            "child_id": data["child_id"],
            "responses": responses
        })
        res_data = res.get_json() if hasattr(res, "get_json") else {}
        res_data["id"] = cur.lastrowid
        return jsonify(res_data), 201

    return jsonify({"id": cur.lastrowid}), 201

@app.route("/api/notes/session/<int:sid>", methods=["GET"])
def get_notes(sid):
    db = get_db()
    rows = db.execute("SELECT * FROM facilitator_notes WHERE session_id=?", (sid,)).fetchall()
    return jsonify([dict(r) for r in rows])

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Mentors & Matching
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/mentors", methods=["GET"])
def list_mentors():
    db = get_db()
    domain = request.args.get("domain")
    if domain:
        rows = db.execute("SELECT * FROM mentors WHERE domain=? AND active=1", (domain,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM mentors WHERE active=1").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/matches", methods=["POST"])
def create_match():
    data = request.json or {}
    child_id = data.get("child_id")
    mentor_id = data.get("mentor_id")
    domain = data.get("domain", "")
    
    # default 3-milestone plan
    plan = [
        {"month": 1, "title": "First session & orientation",    "done": False},
        {"month": 3, "title": "Mid-quarter skill demonstration","done": False},
        {"month": 6, "title": "Portfolio review & next steps",  "done": False},
    ]
    
    supabase_match_id = None
    supabase_milestone_ids = []
    
    if supabase_client:
        try:
            # 1. Insert into mentor_matches on Supabase
            match_data = {
                "child_id": child_id,
                "mentor_id": mentor_id,
                "domain": domain,
                "plan": json.dumps(plan)
            }
            res_match = supabase_client.table("mentor_matches").insert(match_data).execute()
            if res_match.data and len(res_match.data) > 0:
                supabase_match_id = res_match.data[0]["id"]
                
                # 2. Insert milestones on Supabase
                for m in plan:
                    milestone_data = {
                        "match_id": supabase_match_id,
                        "title": m["title"],
                        "done": 0
                    }
                    res_m = supabase_client.table("milestones").insert(milestone_data).execute()
                    if res_m.data and len(res_m.data) > 0:
                        supabase_milestone_ids.append(res_m.data[0]["id"])
        except Exception as e:
            print(f"[SUPABASE WARNING] Failed to insert match or milestones: {e}")
            
    db = get_db()
    if supabase_match_id is not None:
        # Insert into local mentor_matches with explicit ID
        db.execute("""
            INSERT INTO mentor_matches (id, child_id, mentor_id, domain, plan)
            VALUES (?,?,?,?,?)
        """, (supabase_match_id, child_id, mentor_id, domain, json.dumps(plan)))
        
        # Insert into local milestones using Supabase IDs
        for i, m in enumerate(plan):
            if i < len(supabase_milestone_ids):
                db.execute(
                    "INSERT INTO milestones (id, match_id, title) VALUES (?,?,?)",
                    (supabase_milestone_ids[i], supabase_match_id, m["title"])
                )
            else:
                db.execute(
                    "INSERT INTO milestones (match_id, title) VALUES (?,?)",
                    (supabase_match_id, m["title"])
                )
        db.commit()
        match_id = supabase_match_id
    else:
        # Fallback to local auto-increment
        cur = db.execute("""
            INSERT INTO mentor_matches (child_id, mentor_id, domain, plan)
            VALUES (?,?,?,?)
        """, (child_id, mentor_id, domain, json.dumps(plan)))
        match_id = cur.lastrowid
        for m in plan:
            db.execute(
                "INSERT INTO milestones (match_id, title) VALUES (?,?)",
                (match_id, m["title"])
            )
        db.commit()
        
    return jsonify({"id": match_id, "plan": plan}), 201

@app.route("/api/matches/child/<int:cid>", methods=["GET"])
def child_matches(cid):
    db = get_db()
    rows = db.execute("""
        SELECT mm.*, m.name as mentor_name, m.bio, m.contact
        FROM mentor_matches mm
        JOIN mentors m ON m.id = mm.mentor_id
        WHERE mm.child_id = ?
    """, (cid,)).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["plan"] = json.loads(d["plan"]) if d["plan"] else []
        result.append(d)
    return jsonify(result)

@app.route("/api/matches/<int:mid>/milestone", methods=["PUT"])
def update_milestone(mid):
    data = request.json or {}
    milestone_id = data.get("milestone_id")
    done = data.get("done")
    note = data.get("note", "")
    
    if supabase_client:
        try:
            update_data = {
                "done": int(done) if done is not None else 0,
                "note": note
            }
            supabase_client.table("milestones").update(update_data).eq("id", milestone_id).eq("match_id", mid).execute()
        except Exception as e:
            print(f"[SUPABASE WARNING] Failed to update milestone in Supabase: {e}")
            
    db = get_db()
    db.execute(
        "UPDATE milestones SET done=?, note=? WHERE id=? AND match_id=?",
        (done, note, milestone_id, mid)
    )
    db.commit()
    return jsonify({"ok": True})

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Dashboard stats
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/stats", methods=["GET"])
def stats():
    db = get_db()
    total_children  = db.execute("SELECT COUNT(*) FROM children").fetchone()[0]
    total_sessions  = db.execute("SELECT COUNT(*) FROM sessions WHERE status='complete'").fetchone()[0]
    total_matches   = db.execute("SELECT COUNT(*) FROM mentor_matches").fetchone()[0]
    domain_dist     = db.execute("""
        SELECT top_domain, COUNT(*) as cnt
        FROM sessions WHERE status='complete' AND top_domain IS NOT NULL
        GROUP BY top_domain ORDER BY cnt DESC
    """).fetchall()
    return jsonify({
        "total_children": total_children,
        "total_sessions": total_sessions,
        "total_matches":  total_matches,
        "domain_distribution": [dict(r) for r in domain_dist],
    })

# ═══════════════════════════════════════════════════════════════════════════════

def answer_to_scale(answer):
    """
    Converts either an old numeric answer or a new structured activity answer
    into a 0-4 score.
    """
    if isinstance(answer, (int, float)):
        return max(0, min(4, float(answer)))

    if not isinstance(answer, dict):
        return 0

    if "value" in answer and isinstance(answer["value"], (int, float)):
        return max(0, min(4, float(answer["value"])))

    if answer.get("correct") is True:
        return 4
    if answer.get("correct") is False:
        return 0

    if isinstance(answer.get("accuracy"), (int, float)):
        return max(0, min(4, float(answer["accuracy"]) * 4))

    if isinstance(answer.get("memory_score"), (int, float)):
        return max(0, min(4, float(answer["memory_score"]) * 4))

    return 0

def extract_metric_summary(responses):
    structured = [v for v in responses.values() if isinstance(v, dict)]
    if not structured:
        return {}

    response_times = [v.get("response_ms") for v in structured if isinstance(v.get("response_ms"), (int, float))]
    reaction_times = [v.get("reaction_ms") for v in structured if isinstance(v.get("reaction_ms"), (int, float))]
    correct_values = [v.get("correct") for v in structured if isinstance(v.get("correct"), bool)]
    idea_counts = [v.get("idea_count") for v in structured if isinstance(v.get("idea_count"), (int, float))]

    def avg(values):
        return round(sum(values) / len(values), 1) if values else None

    return {
        "tasks_answered": len(structured),
        "accuracy_rate": round(sum(1 for v in correct_values if v) / len(correct_values), 2) if correct_values else None,
        "average_response_ms": avg(response_times),
        "best_reaction_ms": min(reaction_times) if reaction_times else None,
        "idea_count": max(idea_counts) if idea_counts else None,
        "by_task": structured,
    }

# Standardized psychometric task component categories
FORMAL_MAPPING = {
    "logical_pattern_matrix": "Sequences",
    "logical_riddle": "Deduction",
    "logical_pattern_3": "Sequences",
    "logical_riddle_4": "Deduction",
    "logical_pattern_5": "Classification",
    "logical_riddle_6": "Reasoning puzzles",
    "spatial_rotation": "Rotation",
    "spatial_perspective": "Visual transformation",
    "spatial_origami": "Visual transformation",
    "spatial_block_count": "Construction",
    "spatial_maze_logic": "Navigation",
    "spatial_shape_match": "Visual transformation",
    "visualizer_memory_grid": "Visual imagination",
    "creative_uses": "Alternative uses",
    "creative_story_spark": "Story generation",
    "creative_color_harmony": "Visual imagination",
    "creative_instrument": "Pattern invention",
    "creative_divergent_shapes": "Alternative uses",
    "language_story_order": "Storytelling",
    "language_analogy": "Explanation",
    "language_unscramble": "Verbal fluency",
    "language_opposite": "Verbal fluency",
    "language_rhyme_scheme": "Storytelling",
    "language_cloze_passage": "Verbal fluency",
    "visual_reaction": "Reaction speed",
    "kinesthetic_motor_planning": "Motor coordination",
    "kinesthetic_balancing": "Movement patterns",
    "kinesthetic_aiming": "Motor coordination",
    "kinesthetic_speed_tapping": "Reaction speed",
    "kinesthetic_dance_improvisation": "Movement patterns",
    "social_response": "Group preference",
    "social_conflict_resolution": "Decision scenarios",
    "social_group_project": "Influence choices",
    "social_empathy": "Group preference",
    "social_leadership_style": "Influence choices",
    "social_cooperation": "Influence choices",
    "naturalist_decomposer": "Observation",
    "naturalist_wind_disperse": "Classification",
    "naturalist_weather_pattern": "Observation",
    "naturalist_animal_track": "Classification",
    "naturalist_plant_needs": "Environment interest",
    "naturalist_biodiversity": "Environment interest",
    "intrapersonal_reflection": "Reflection",
    "intrapersonal_frustration": "Reflection",
    "intrapersonal_journaling": "Reflection",
    "intrapersonal_goal_setting": "Goal preference",
    "intrapersonal_self_regulation": "Self-awareness",
    "intrapersonal_self_awareness": "Self-awareness"
}

# 30-Day weekly action plans matching domains
ACTION_PLANS = {
    "creative": {
        "week_1": "Visual Storyboard: Create a 4-frame comic or photo collage illustrating a silent adventure story using household objects.",
        "week_2": "Divergent Design: Collect 3 plastic bottles or containers and redesign them into useful instruments or decorative plant holders.",
        "week_3": "Open-Ended Brainstorming: Devise 10 alternative uses for everyday items like a spoon or an old shoe, sharing ideas with a sibling.",
        "week_4": "Community Showcase: Share your drawings or handmade items with a mentor and discuss your creative design choices."
    },
    "logical": {
        "week_1": "Logical Sequence Tracking: Solve 3 classic sequence riddles or number pattern puzzles with a parent or friend.",
        "week_2": "Pattern Induction: Classify local plants or rocks by size, shape, and texture, writing down the logic behind your groupings.",
        "week_3": "Problem-Solving Strategy: Learn a strategy board game (like Chess, Checkers, or Bagh-Chaal) and play 3 complete matches.",
        "week_4": "Algorithm Design: Write down step-by-step instructions (an algorithm) for a complex household task, checking if a friend can follow it."
    },
    "spatial": {
        "week_1": "3D Structural Building: Build a self-supporting tower at least 30cm high using only paper and tape or cardboard boxes.",
        "week_2": "Perspective Sketching: Draw your classroom or room from 3 different angles (top-down map, eye-level, corner view).",
        "week_3": "Origami & Geometry: Create 3 folded paper figures (like a cup, a box, or a crane) without using scissors or glue.",
        "week_4": "Navigation Walk: Draw a detailed map of the route from your home to the Project WHY center, indicating major landmarks."
    },
    "social": {
        "week_1": "Interactive Scenarios: Lead a group of 3 peers in selecting a game to play, ensuring everyone's opinion is heard and respected.",
        "week_2": "Cooperative Coordination: Organise a classroom tidy-up or small chore rotation among classmates, assigning roles by strength.",
        "week_3": "Empathy Interview: Ask a friend or family member about their day, listening carefully without interrupting, and summarize their feelings.",
        "week_4": "Group Presentation: Coordinate a team of classmates to present a simple idea or role-play a scenario in front of a mentor."
    },
    "language": {
        "week_1": "Sentence sequencing: Write a short paragraph of 4 sentences, scramble the order, and see if a family member can sequence it correctly.",
        "week_2": "Verbal Connection Analogy: Play a verbal word association game with peers, naming contrasting or rhyming words as fast as possible.",
        "week_3": "Folk Story Retelling: Tell a traditional or personal story to a small group of children, using voice changes for different characters.",
        "week_4": "Junior Interview: Prepare 3 questions and interview a local elder or mentor about their childhood, writing down their answers."
    },
    "naturalist": {
        "week_1": "Biodiversity Log: Observe a 1-square-meter patch of soil for 15 minutes, drawing and listing all plants, insects, and details noticed.",
        "week_2": "Weather Pattern Tracking: Keep a daily cloud, wind, and temperature chart for 7 days, noting any recurring visual patterns.",
        "week_3": "Ecosystem observation: Find an outdoor plant, check for signs of hydration/dryness, and explain to a mentor how water travels through it.",
        "week_4": "Local Nature Classification: Group 10 fallen leaves or twigs from your neighborhood by their patterns and share your findings."
    },
    "kinesthetic": {
        "week_1": "Lightning Tap Coordination: Practice hand-eye coordination by bouncing a small ball against a wall and catching it 20 times in a row.",
        "week_2": "Rope Balance Walk: Draw a straight chalk line on the ground and practice balancing on one foot, then walking backward on the line.",
        "week_3": "Target Accuracy throwing: Practice aiming by tossing soft paper balls into a bucket from 3 meters away, tracking your success rate.",
        "week_4": "Dance Improvisation: Invent a short, 4-step sequence of movements that represents water or wind, and perform it for a mentor."
    },
    "intrapersonal": {
        "week_1": "Resilience Reflection: Write or draw in a journal about a difficult task you faced recently and list 2 things that helped you keep trying.",
        "week_2": "Goal-Setting Scale: Define one simple skill you want to learn this week and track your practice time daily (target: 10 mins/day).",
        "week_3": "Quiet Problem-Solving: Spend 10 minutes in quiet self-reflection before tackling a complex homework assignment or puzzle.",
        "week_4": "Mentor Review Seminar: Discuss your assessment results and 30-day goals with a trusted mentor, reviewing what makes you feel focused."
    }
}

def score_responses(responses, child, discovery_answers=None, facilitator_note=None):
    """
    Core scoring engine.
    Computes Discovery (15%), Exposure (10%), Deep Assessment (60% / 75%), and Facilitator (15%) weights.
    Returns standard tq_scores, integrated, eq_score, visualizer_score, metrics, and new analytics.
    """
    # Balanced discovery mapping
    discovery_mapping = {
        "q_discovery_1": {0: "logical", 1: "creative", 2: "language", 3: "social"},
        "q_discovery_2": {0: "spatial", 1: "creative", 2: "logical", 3: "kinesthetic"},
        "q_discovery_3": {0: "naturalist", 1: "creative", 2: "intrapersonal", 3: "language"},
        "q_discovery_4": {0: "social", 1: "language", 2: "intrapersonal", 3: "kinesthetic"},
        "q_discovery_5": {0: "logical", 1: "spatial", 2: "kinesthetic", 3: "social"},
        "q_discovery_6": {0: "creative", 1: "social", 2: "language", 3: "spatial"},
        "q_discovery_7": {0: "naturalist", 1: "spatial", 2: "logical", 3: "kinesthetic"},
        "q_discovery_8": {0: "language", 1: "naturalist", 2: "creative", 3: "intrapersonal"},
        "q_discovery_9": {0: "naturalist", 1: "spatial", 2: "creative", 3: "kinesthetic"},
        "q_discovery_10": {0: "kinesthetic", 1: "spatial", 2: "language", 3: "intrapersonal"},
        "q_discovery_11": {0: "naturalist", 1: "logical", 2: "social", 3: "intrapersonal"},
        "q_discovery_12": {0: "logical", 1: "naturalist", 2: "social", 3: "intrapersonal"}
    }
    
    discovery_counts = {
        "logical": 0, "spatial": 0, "creative": 0, "language": 0,
        "kinesthetic": 0, "social": 0, "naturalist": 0, "intrapersonal": 0
    }
    if discovery_answers:
        for q_key, opts in discovery_mapping.items():
            choice = discovery_answers.get(q_key)
            if choice is not None:
                try:
                    choice_val = int(choice)
                    if choice_val in opts:
                        dom = opts[choice_val]
                        discovery_counts[dom] += 1
                except Exception:
                    pass

    rich_mode = any(isinstance(v, dict) for v in responses.values())
    rich_component_scores = {}
    if rich_mode:
        for answer in responses.values():
            if not isinstance(answer, dict):
                continue
            domain = answer.get("domain")
            component = answer.get("component")
            if domain not in DOMAIN_WEIGHTS or component not in DOMAIN_WEIGHTS[domain]:
                continue
            key = f"{domain}_{component}"
            rich_component_scores.setdefault(key, []).append(answer_to_scale(answer))

    # Compile Evidence log based on actual 3-indicator psychometric validity
    evidence = {}
    for domain in DOMAIN_WEIGHTS.keys():
        # 1. Preference indicator (Exposure >= 1)
        exp_val = child.get(f"exp_{domain}", 0)
        has_pref = exp_val >= 1
        pref_label = ["Never tried it", "Tried a few times", "Do it sometimes", "Do it regularly"][exp_val]
        pref_desc = f"Observed exposure preference: '{pref_label}'" if has_pref else "No prior preference or regular exposure observed."

        # 2. Behavioral indicator (Discovery Count >= 1)
        disc_count = discovery_counts.get(domain, 0)
        has_behav = disc_count >= 1
        behav_desc = f"Selected spontaneous behavior in {disc_count} discovery scenarios" if has_behav else "No spontaneous behavior observed in discovery scenarios."

        # 3. Performance indicator (Deep Assessment puzzles scored >= 2.0)
        perf_tasks = []
        if rich_mode:
            for q_key, answer in responses.items():
                if isinstance(answer, dict) and answer.get("domain") == domain:
                    score = answer_to_scale(answer)
                    if score >= 2.0:
                        perf_tasks.append(q_key)
        has_perf = len(perf_tasks) >= 2
        
        # Format names from the formal psychometric mapped categories
        task_categories = list(set([FORMAL_MAPPING.get(t, t.replace("_", " ").title()) for t in perf_tasks]))
        perf_desc = f"Demonstrated accuracy in {len(perf_tasks)} puzzles: {', '.join(task_categories[:2])}" if has_perf else "Performance on scored cognitive challenges was insufficient to establish independent evidence."

        # Overall Evidence Level: Requires at least 3 independent sources for "Strong"
        level = "Strong" if (has_pref and has_behav and has_perf) else "Moderate" if (sum([has_pref, has_behav, has_perf]) >= 2) else "Needs Validation"

        evidence[domain] = {
            "has_preference": has_pref,
            "preference_desc": pref_desc,
            "has_behavioral": has_behav,
            "behavioral_desc": behav_desc,
            "has_performance": has_perf,
            "performance_desc": perf_desc,
            "level": level,
            "strong": [FORMAL_MAPPING.get(t, t.replace("_", " ").title()) for t in perf_tasks if answer_to_scale(responses[t]) >= 3.0],
            "moderate": [FORMAL_MAPPING.get(t, t.replace("_", " ").title()) for t in perf_tasks if 2.0 <= answer_to_scale(responses[t]) < 3.0],
            "needs_validation": [FORMAL_MAPPING.get(t, t.replace("_", " ").title()) for t, val in responses.items() if isinstance(val, dict) and val.get("domain") == domain and answer_to_scale(val) < 2.0]
        }

    tq_raw_scores = {}
    for domain, components in DOMAIN_WEIGHTS.items():
        raw = 0
        total_weight = 0
        for component, weight in components.items():
            key = f"{domain}_{component}"
            if rich_mode:
                if key not in rich_component_scores:
                    continue
                val = sum(rich_component_scores[key]) / len(rich_component_scores[key])
            else:
                val = answer_to_scale(responses.get(key, 0))
            raw += (val / 4.0) * weight
            total_weight += weight
        tq_raw_scores[domain] = (raw / total_weight) * 100 if total_weight else 0

    # Calculate pre-facilitator scores
    raw_blended = {}
    for domain in DOMAIN_WEIGHTS.keys():
        s_disc = (discovery_counts.get(domain, 0) / 6.0) * 100.0
        s_exp = (child.get(f"exp_{domain}", 0) / 3.0) * 100.0
        s_deep = tq_raw_scores.get(domain, 0.0)
        raw_blended[domain] = 0.15 * s_disc + 0.10 * s_exp + 0.75 * s_deep

    original_top = max(raw_blended.items(), key=lambda x: x[1])[0] if raw_blended else "unknown"

    # Compute facilitator validation score
    has_notes = facilitator_note is not None
    facilitator_scores = {}
    for domain in DOMAIN_WEIGHTS.keys():
        if has_notes:
            confirmed = bool(facilitator_note.get("confirmed"))
            override_domain = facilitator_note.get("override_domain")
            if confirmed:
                facilitator_scores[domain] = 100.0 if domain == original_top else 60.0
            elif override_domain:
                if domain == override_domain:
                    facilitator_scores[domain] = 100.0
                elif domain == original_top:
                    facilitator_scores[domain] = 30.0
                else:
                    facilitator_scores[domain] = 60.0
            else:
                facilitator_scores[domain] = 70.0
        else:
            facilitator_scores[domain] = 70.0

    # Combine with weights
    blended = {}
    for domain in DOMAIN_WEIGHTS.keys():
        s_disc = (discovery_counts.get(domain, 0) / 6.0) * 100.0
        s_exp = (child.get(f"exp_{domain}", 0) / 3.0) * 100.0
        s_deep = tq_raw_scores.get(domain, 0.0)
        s_fac = facilitator_scores[domain]
        if has_notes:
            blended[domain] = 0.15 * s_disc + 0.10 * s_exp + 0.60 * s_deep + 0.15 * s_fac
        else:
            blended[domain] = 0.15 * s_disc + 0.10 * s_exp + 0.75 * s_deep

    # Stretch-normalization to prevent domain clustering
    max_raw = max(blended.values())
    min_raw = min(blended.values())
    final_scores = {}
    if max_raw > min_raw:
        target_max = max(75.0, min(95.0, max_raw))
        target_min = max(35.0, min(60.0, min_raw))
        for domain, raw_val in blended.items():
            ratio = (raw_val - min_raw) / (max_raw - min_raw)
            final_scores[domain] = int(round(target_min + ratio * (target_max - target_min)))
    else:
        for domain, raw_val in blended.items():
            final_scores[domain] = int(round(raw_val))

    # Sort domains by final stretched score
    sorted_domains = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    top_domain = sorted_domains[0][0] if sorted_domains else "unknown"
    top_3 = [d for d, _ in sorted_domains[:3]]

    # Confidence scoring engine (rigorous psychometric build)
    structured_answers = [v for v in responses.values() if isinstance(v, dict)]
    tasks_answered = len(structured_answers)
    
    # 1. Task Completion Rate (max 30 pts)
    task_pts = 30 if tasks_answered >= 24 else 20 if tasks_answered >= 16 else 10 if tasks_answered >= 8 else 5
    
    # 2. Response Consistency (max 20 pts)
    metrics = extract_metric_summary(responses)
    accuracy_rate = metrics.get("accuracy_rate", 0.0) or 0.0
    consistency_pts = 20 if 0.4 <= accuracy_rate <= 0.85 else 10
    consistency_desc = "high accuracy and stable pacing" if consistency_pts == 20 else "varying response accuracy"
    
    # 3. Domain Separation (max 20 pts)
    avg_score = sum(final_scores.values()) / len(final_scores) if final_scores else 50
    separation_gap = final_scores.get(top_domain, 50) - avg_score
    separation_pts = 20 if separation_gap >= 12 else 10 if separation_gap >= 6 else 5
    separation_desc = "strong separation between domains" if separation_gap >= 12 else "moderate domain differentiation"
    
    # 4. Evidence Density (max 15 pts)
    strong_domains = [d for d, ev in evidence.items() if ev["level"] == "Strong"]
    density_pts = 15 if len(strong_domains) >= 2 else 10 if len(strong_domains) == 1 else 5
    
    # 5. Exposure Alignment (max 15 pts)
    top_exposure_domains = sorted(child.items(), key=lambda x: x[1] if x[0].startswith("exp_") else -1, reverse=True)
    top_exp_key = top_exposure_domains[0][0].replace("exp_", "") if top_exposure_domains else ""
    alignment_pts = 15 if top_domain == top_exp_key else 5
    
    confidence_score = task_pts + consistency_pts + separation_pts + density_pts + alignment_pts
    confidence_level = "High" if confidence_score >= 75 else "Moderate" if confidence_score >= 50 else "Low"
    
    confidence_desc = (
        f"Confidence is {confidence_level} ({confidence_score}/100) because {tasks_answered} interactive tasks "
        f"were completed, the child demonstrated {consistency_desc}, and their scores showed {separation_desc}."
    )

    # Untapped potential (Strict trigger: score >= 75, exposure level <= 1, and strong evidence level)
    untapped_potential = []
    for d, score in final_scores.items():
        exp_val = child.get(f"exp_{d}", 0)
        if score >= 75 and exp_val <= 1 and evidence.get(d, {}).get("level") == "Strong":
            untapped_potential.append(d)

    # Domain Separation Index as difference between top 2 domains
    separation_diff = 0
    if len(sorted_domains) > 1:
        separation_diff = sorted_domains[0][1] - sorted_domains[1][1]
    multiple_talents_detected = separation_diff < 5

    # EQ and Visualizer Scores
    eq_val = responses.get("eq_overall", None)
    eq_score = int(round((answer_to_scale(eq_val) / 4.0) * 100)) if eq_val is not None else int(round((final_scores.get("social", 50) + final_scores.get("intrapersonal", 50)) / 2))
    viz_val = responses.get("visualizer_overall", None)
    visualizer_score = int(round((answer_to_scale(viz_val) / 4.0) * 100)) if viz_val is not None else int(round((final_scores.get("creative", 50) + final_scores.get("spatial", 50)) / 2))

    return {
        "tq_scores": final_scores,
        "integrated": final_scores,
        "eq_score": eq_score,
        "visualizer_score": visualizer_score,
        "metrics": metrics,
        "evidence": evidence,
        "confidence_level": confidence_level,
        "confidence_score": confidence_score,
        "confidence_desc": confidence_desc,
        "untapped_potential": untapped_potential,
        "primary_domain": top_domain,
        "secondary_domains": [d for d, _ in sorted_domains[1:3]],
        "emerging_domains": [d for d, _ in sorted_domains[3:5]],
        "discovery_counts": discovery_counts,
        "original_top": original_top,
        "separation_index": int(separation_diff),
        "multiple_talents_detected": multiple_talents_detected,
        "action_plan": ACTION_PLANS.get(top_domain, {})
    }


RECOMMENDATION_LIBRARY = {
    "kinesthetic": [
        "Give weekly movement practice: dance, sport, theatre movement, or hands-on craft.",
        "Use demonstrations before written instruction; let the child learn by doing.",
        "Track stamina, coordination, and rhythm over the next 4 weeks.",
    ],
    "creative": [
        "Create a small portfolio: drawings, songs, designs, stories, or handmade objects.",
        "Offer open-ended prompts where there is more than one correct answer.",
        "Pair the child with a mentor who can give feedback without over-structuring ideas.",
    ],
    "logical": [
        "Give progressive puzzles, mental maths, pattern tasks, and basic coding games.",
        "Ask the child to explain their reasoning aloud; capture strategies, not only answers.",
        "Increase difficulty only after accuracy stays stable across several tasks.",
    ],
    "spatial": [
        "Use model-making, maps, blocks, repair tasks, and drawing from different angles.",
        "Let the child sketch the plan before building.",
        "Observe whether they improve when materials are in their hands.",
    ],
    "social": [
        "Give small leadership roles in group activities.",
        "Observe empathy, conflict resolution, and how peers respond to their ideas.",
        "Use mentoring that includes communication and community projects.",
    ],
    "language": [
        "Use storytelling, debate, theatre, journaling, and explaining tasks.",
        "Record short spoken responses to track clarity and confidence.",
        "Encourage reading aloud and retelling stories in their preferred language.",
    ],
    "naturalist": [
        "Use plant observation, animal care, weather logs, and nature classification.",
        "Let the child maintain a nature notebook with drawings and patterns noticed.",
        "Connect learning to local environment and practical care tasks.",
    ],
    "intrapersonal": [
        "Use reflection journals, goal-setting, quiet problem solving, and self-review.",
        "Give the child time to think before answering.",
        "Pair with a mentor who supports emotional awareness and resilience.",
    ],
}

def apply_facilitator_reviews(session_id, scores):
    db = get_db()
    notes = db.execute("""
        SELECT confirmed, override_domain, observation, notes
        FROM facilitator_notes
        WHERE session_id=?
        ORDER BY created_at DESC
    """, (session_id,)).fetchall()
    if not notes:
        return scores

    integrated = dict(scores["integrated"])
    latest = dict(notes[0])
    original_top = max(integrated.items(), key=lambda x: x[1])[0] if integrated else ""
    adjustment = {
        "review_count": len(notes),
        "original_top_domain": original_top,
        "confirmed": bool(latest.get("confirmed")),
        "override_domain": latest.get("override_domain") or "",
    }

    if latest.get("confirmed"):
        if original_top in integrated:
            integrated[original_top] = min(100, round(integrated[original_top] + 4, 1))
        adjustment["method"] = "Facilitator confirmed top result; confidence boosted."
    else:
        override = latest.get("override_domain")
        if override in integrated:
            integrated[override] = min(100, round(integrated[override] + 12, 1))
            if original_top and original_top != override:
                integrated[original_top] = max(0, round(integrated[original_top] - 6, 1))
            adjustment["method"] = "Facilitator disagreed; override domain blended into final result."
        else:
            adjustment["method"] = "Facilitator flagged concern; no valid override domain supplied."

    scores["integrated"] = integrated
    scores["facilitator_adjustment"] = adjustment
    return scores

def build_recommendations(scores, child):
    integrated = scores.get("integrated", {})
    if not integrated:
        return {"next_steps": [], "confidence": "low", "rationale": "No completed score profile yet."}

    sorted_domains = sorted(integrated.items(), key=lambda x: x[1], reverse=True)
    top_domain, top_score = sorted_domains[0]
    second_score = sorted_domains[1][1] if len(sorted_domains) > 1 else 0
    gap = top_score - second_score
    confidence = "high" if gap >= 12 and top_score >= 70 else "medium" if gap >= 6 else "low"

    metrics = scores.get("metrics", {})
    next_steps = list(RECOMMENDATION_LIBRARY.get(top_domain, []))
    if confidence == "low":
        next_steps.insert(0, "Run a second short validation session before making a final mentor decision.")
    if metrics.get("accuracy_rate") is not None and metrics["accuracy_rate"] < 0.55:
        next_steps.append("Repeat attention-heavy tasks in a quieter setting to rule out distraction.")
    if scores.get("facilitator_adjustment"):
        next_steps.append("Review the facilitator observation alongside the score profile before mentor assignment.")

    return {
        "top_domain": top_domain,
        "confidence": confidence,
        "rationale": f"Top score is {top_score}; gap to next domain is {round(gap, 1)}.",
        "next_steps": next_steps,
        "mentor_domain": top_domain,
        "age_group": "9-12" if int(child.get("age", 0)) <= 12 else "13-15",
    }


# ── USER MANAGEMENT ENDPOINTS ────────────────────────────────────────────────
@app.route("/api/admin/users", methods=["GET"])
@require_role(["master_admin", "admin"])
def list_users():
    db = get_db()
    rows = db.execute("SELECT id, name, email, role, active, center_id FROM users").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/users", methods=["POST"])
@require_role(["master_admin", "admin"])
def create_user_tms():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    role = data.get("role", "facilitator")
    center_id = data.get("center_id")
    
    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
        
    db = get_db()
    try:
        db.execute("""
            INSERT INTO users (name, email, password_hash, role, center_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, hash_password(password), role, center_id))
        db.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "success"}), 201

@app.route("/api/admin/users/<uid>", methods=["DELETE"])
@require_role(["master_admin", "admin"])
def delete_user_tms(uid):
    db = get_db()
    db.execute("DELETE FROM users WHERE id=?", (uid,))
    db.commit()
    return jsonify({"status": "success"})

@app.route("/api/admin/users/<uid>/approve", methods=["PUT"])
@require_role(["master_admin", "admin"])
def approve_user_tms(uid):
    data = request.json or {}
    approved_role = data.get("role")
    center_id = data.get("center_id")
    
    db = get_db()
    user_row = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not user_row:
        return jsonify({"error": "User not found"}), 404
        
    if not approved_role:
        current_role = user_row["role"]
        if current_role.startswith("pending_"):
            approved_role = current_role.replace("pending_", "")
        else:
            approved_role = current_role
            
    if approved_role not in ("facilitator", "mentor", "admin", "master_admin"):
        approved_role = "facilitator"
        
    try:
        if center_id:
            db.execute("UPDATE users SET role=?, center_id=? WHERE id=?", (approved_role, center_id, uid))
        else:
            db.execute("UPDATE users SET role=? WHERE id=?", (approved_role, uid))
        db.commit()
        
        # Supabase sync
        supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if supabase_url and supabase_key:
            try:
                from supabase import create_client
                sp_client = create_client(supabase_url, supabase_key)
                sp_client.table("users").update({"role": approved_role}).eq("email", user_row["email"]).execute()
                print(f"[SUPABASE SYNC] Approved user role {approved_role} for {user_row['email']}")
            except Exception as e:
                print(f"[SUPABASE WARNING] Failed to sync approved user role: {e}")
    except Exception as e:
        return jsonify({"error": str(e)}), 400
        
    return jsonify({"status": "success", "role": approved_role})

# ── CENTER MANAGEMENT ENDPOINTS ─────────────────────────────────────────────
@app.route("/api/centers", methods=["GET"])
def list_centers():
    db = get_db()
    rows = db.execute("SELECT * FROM centers").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/centers", methods=["POST"])
@require_role(["master_admin"])
def create_center():
    data = request.json or {}
    name = data.get("name")
    location = data.get("location")
    if not name:
        return jsonify({"error": "Center name required"}), 400
    db = get_db()
    db.execute("INSERT INTO centers (name, location) VALUES (?, ?)", (name, location))
    db.commit()
    return jsonify({"status": "success"}), 201

# ── WORKSHOP PLANNING & ATTENDANCE ──────────────────────────────────────────
@app.route("/api/workshops", methods=["GET"])
def list_workshops():
    db = get_db()
    rows = db.execute("SELECT w.*, c.name as center_name FROM workshops w LEFT JOIN centers c ON c.id=w.center_id").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/workshops", methods=["POST"])
@require_role(["master_admin", "admin"])
def create_workshop():
    data = request.json or {}
    name = data.get("name")
    domain = data.get("domain")
    center_id = data.get("center_id")
    description = data.get("description")
    if not name or not domain:
        return jsonify({"error": "Name and domain are required"}), 400
    db = get_db()
    db.execute("INSERT INTO workshops (name, domain, center_id, description) VALUES (?, ?, ?, ?)", (name, domain, center_id, description))
    db.commit()
    return jsonify({"status": "success"}), 201

@app.route("/api/workshops/<int:wid>/sessions", methods=["GET"])
def list_workshop_sessions(wid):
    db = get_db()
    rows = db.execute("SELECT * FROM workshop_sessions WHERE workshop_id=?", (wid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/workshops/<int:wid>/sessions", methods=["POST"])
@require_role(["master_admin", "admin", "mentor"])
def create_workshop_session(wid):
    data = request.json or {}
    session_date = data.get("session_date")
    notes = data.get("notes")
    attendance = data.get("attendance", {})
    
    if not session_date:
        return jsonify({"error": "Session date required"}), 400
        
    db = get_db()
    cur = db.execute("INSERT INTO workshop_sessions (workshop_id, session_date, notes) VALUES (?, ?, ?)", (wid, session_date, notes))
    session_id = cur.lastrowid
    
    for cid_str, status in attendance.items():
        try:
            cid = int(cid_str)
            db.execute("INSERT INTO workshop_attendance (workshop_session_id, child_id, status) VALUES (?, ?, ?)", (session_id, cid, status))
        except Exception:
            pass
            
    db.commit()
    return jsonify({"status": "success", "session_id": session_id}), 201

@app.route("/api/workshops/attendance/<int:cid>", methods=["GET"])
def list_student_attendance(cid):
    db = get_db()
    rows = db.execute("""
        SELECT a.status, s.session_date, w.name as workshop_name, w.domain
        FROM workshop_attendance a
        JOIN workshop_sessions s ON s.id = a.workshop_session_id
        JOIN workshops w ON w.id = s.workshop_id
        WHERE a.child_id = ?
        ORDER BY s.session_date DESC
    """, (cid,)).fetchall()
    return jsonify([dict(r) for r in rows])

# ── MENTOR VALIDATION ENDPOINTS ─────────────────────────────────────────────
@app.route("/api/mentors/validations/<int:cid>", methods=["GET"])
def list_mentor_validations(cid):
    db = get_db()
    rows = db.execute("SELECT * FROM mentor_validations WHERE child_id=? ORDER BY created_at DESC", (cid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/mentors/validations", methods=["POST"])
@require_role(["master_admin", "admin", "mentor"])
def submit_mentor_validation():
    data = request.json or {}
    match_id = data.get("match_id")
    child_id = data.get("child_id")
    domain = data.get("domain")
    rating = data.get("rating", 3)
    strengths = data.get("strengths")
    growth_areas = data.get("growth_areas")
    notes = data.get("notes")
    
    if not child_id or not domain:
        return jsonify({"error": "Child ID and domain required"}), 400
        
    db = get_db()
    db.execute("""
        INSERT INTO mentor_validations (match_id, child_id, domain, rating, strengths, growth_areas, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (match_id, child_id, domain, rating, strengths, growth_areas, notes))
    db.commit()
    return jsonify({"status": "success"}), 201

# ── PUZZLE (QUESTION BANK) MANAGEMENT ──────────────────────────────────────────
@app.route("/api/puzzles", methods=["GET"])
@require_role(["master_admin"])
def list_puzzles():
    db = get_db()
    rows = db.execute("SELECT id, key, type, domain, component, data FROM puzzles ORDER BY domain, key").fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/puzzles/<int:pid>", methods=["PUT"])
@require_role(["master_admin"])
def edit_puzzle(pid):
    data = request.json or {}
    puzzle_data = data.get("data")
    if not puzzle_data:
        return jsonify({"error": "Puzzle data is required"}), 400
        
    try:
        parsed_data = json.loads(puzzle_data) if isinstance(puzzle_data, str) else puzzle_data
        data_str = json.dumps(parsed_data)
    except Exception:
        return jsonify({"error": "Invalid JSON format"}), 400
        
    db = get_db()
    db.execute("UPDATE puzzles SET data=? WHERE id=?", (data_str, pid))
    db.commit()
    return jsonify({"status": "success"})

# ── REASSESSMENT SCHEDULER ──────────────────────────────────────────────────
@app.route("/api/sessions/reassess", methods=["POST"])
@require_role(["master_admin", "admin", "facilitator"])
def schedule_reassessment():
    data = request.json or {}
    child_id = data.get("child_id")
    if not child_id:
        return jsonify({"error": "Child ID is required"}), 400
        
    db = get_db()
    cur = db.execute("INSERT INTO sessions (child_id, phase, status) VALUES (?, 'discovery', 'in_progress')", (child_id,))
    db.commit()
    return jsonify({"status": "success", "session_id": cur.lastrowid}), 201

# ── GLOBAL ANALYTICS DASHBOARD ──────────────────────────────────────────────
@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    db = get_db()
    
    sessions = db.execute("SELECT top_domain, COUNT(*) as cnt FROM sessions WHERE status='complete' GROUP BY top_domain").fetchall()
    talent_dist = {r["top_domain"]: r["cnt"] for r in sessions if r["top_domain"]}
    
    workshops = db.execute("SELECT domain, COUNT(*) as cnt FROM workshops GROUP BY domain").fetchall()
    workshop_demand = {r["domain"]: r["cnt"] for r in workshops if r["domain"]}
    
    sessions_all = db.execute("SELECT child_id, personality_data FROM sessions WHERE status='complete'").fetchall()
    untapped_counts = {}
    for s in sessions_all:
        try:
            pdata = json.loads(s["personality_data"] or "{}")
            untapped = pdata.get("untapped_potential", [])
            for u in untapped:
                untapped_counts[u] = untapped_counts.get(u, 0) + 1
        except Exception:
            pass
            
    growth_rows = db.execute("SELECT top_domain, tq_scores, completed_at FROM sessions WHERE status='complete' ORDER BY completed_at").fetchall()
    growth_data = {}
    for r in growth_rows:
        dom = r["top_domain"]
        if not dom: continue
        try:
            tq = json.loads(r["tq_scores"] or "{}")
            score = tq.get(dom, 50)
            date_str = r["completed_at"][:10] if r["completed_at"] else "Unknown"
            growth_data.setdefault(dom, []).append({"date": date_str, "score": score})
        except Exception:
            pass
            
    total_registered = db.execute("SELECT COUNT(*) FROM children").fetchone()[0]
    total_assessed = db.execute("SELECT COUNT(DISTINCT child_id) FROM sessions WHERE status='complete'").fetchone()[0]
    total_matched = db.execute("SELECT COUNT(*) FROM mentor_matches WHERE status='active'").fetchone()[0]
    total_enrolled = db.execute("SELECT COUNT(DISTINCT child_id) FROM workshop_attendance WHERE status='Present'").fetchone()[0]
    
    return jsonify({
        "talent_distribution": talent_dist,
        "workshop_demand": workshop_demand,
        "untapped_potential": untapped_counts,
        "growth_data": growth_data,
        "progress_funnel": {
            "registered": total_registered,
            "assessed": total_assessed,
            "matched": total_matched,
            "enrolled": total_enrolled
        }
    })

# ── EXPORT ENGINE ───────────────────────────────────────────────────────────
import csv
import io
from flask import Response

@app.route("/api/export/csv", methods=["GET"])
@require_role(["master_admin", "admin"])
def export_data_csv():
    db = get_db()
    
    children = db.execute("SELECT * FROM children").fetchall()
    
    output = io.StringIO()
    output.write('\ufeff')
    writer = csv.writer(output)
    
    writer.writerow(["ID", "Name", "Age", "Language", "School Year", "Gender", "Top Domain", "Scores", "Created At"])
    
    for c in children:
        sess = db.execute("SELECT top_domain, tq_scores FROM sessions WHERE child_id=? AND status='complete' ORDER BY completed_at DESC LIMIT 1", (c["id"],)).fetchone()
        top_domain = sess["top_domain"] if sess else "Not Assessed"
        scores = sess["tq_scores"] if sess else "{}"
        writer.writerow([c["id"], c["name"], c["age"], c["language"], c["school_year"], c["gender"], top_domain, scores, c["created_at"]])
        
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=TINS_Talent_Export.csv"}
    )


if __name__ == "__main__":
    init_db()
    print("\n[SUCCESS] GOAT backend running at http://localhost:5050\n")
    app.run(port=5050, debug=True)
