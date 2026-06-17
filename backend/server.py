"""
GOAT Backend — Flask + SQLite
Greatest of All Talents System
"""
import os
import sqlite3
import json
import hashlib
import secrets
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from supabase import create_client, Client

load_dotenv()

# Automatically rewrite IPv6 direct connection to IPv4 pooler connection string if present
db_url = os.environ.get("DATABASE_URL")
if db_url and "db.ubsjcfaokemckctswnzi.supabase.co" in db_url:
    import re
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    # Match password and database name from postgresql://postgres:PASSWORD@db.ubsjcfaokemckctswnzi.supabase.co:5432/DBNAME
    match = re.search(r"postgresql://postgres:([^@]+)@db\.ubsjcfaokemckctswnzi\.supabase\.co:5432/(.+)", db_url)
    if match:
        password = match.group(1)
        dbname = match.group(2)
        project_ref = "ubsjcfaokemckctswnzi"
        
        # Default fallback values (verified working for this project)
        pooler_host = "aws-1-ap-southeast-2.pooler.supabase.com"
        pooler_port = 6543
        
        # Try to dynamically query the Supabase Management API if token is available
        access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
        if access_token:
            try:
                import urllib.request
                import json
                api_url = f"https://api.supabase.com/v1/projects/{project_ref}/config/database/pooler"
                req = urllib.request.Request(
                    api_url, 
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    if isinstance(res_data, list) and len(res_data) > 0:
                        config = res_data[0]
                        pooler_host = config.get("db_host") or pooler_host
                        pooler_port = config.get("db_port") or pooler_port
                        print(f"[DATABASE INFO] Dynamically fetched pooler settings: {pooler_host}:{pooler_port}")
            except Exception as api_err:
                print(f"[DATABASE WARNING] Failed to dynamically fetch pooler configuration: {api_err}. Using hardcoded fallback.")
        
        rewritten_url = f"postgresql://postgres.{project_ref}:{password}@{pooler_host}:{pooler_port}/{dbname}"
        os.environ["DATABASE_URL"] = rewritten_url
        print(f"[DATABASE INFO] Rewrote DATABASE_URL from IPv6 direct connection to IPv4 Connection Pooler ({pooler_host}:{pooler_port}).")

# --- Supabase Client Initialization ---
supabase = None
supabase_client = None

try:
    # 1. Fetch from Render environment variable OR use your project URL fallback
    supabase_url = os.environ.get("SUPABASE_URL") or "https://ubsjcfaokemckctswnzi.supabase.co"
    
    # 2. Fetch from Render environment variable
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        supabase_client = supabase
        print("[SUCCESS] Python Supabase client initialized.")
    else:
        print("[DATABASE WARNING] Supabase URL or Key missing.")
except Exception as e:
    print(f"[DATABASE WARNING] Failed to initialize Supabase client: {e}")

app = Flask(__name__)
CORS(app)  # Enables standard cross-origin configuration automatically

class ApiFallbackMiddleware(object):
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        
    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        if path and path != '/' and not path.startswith('/api/'):
            environ['PATH_INFO'] = '/api' + path
        return self.wsgi_app(environ, start_response)

app.wsgi_app = ApiFallbackMiddleware(app.wsgi_app)

@app.route("/auth/login", methods=["POST", "OPTIONS"])
@app.route("/auth/login-supabase", methods=["POST", "OPTIONS"])
@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
@app.route("/api/auth/login-supabase", methods=["POST", "OPTIONS"])
def auth_login_gate():
    if request.method == "OPTIONS":
        return jsonify({"status": "CORS_PREFLIGHT_OK"}), 200
        
    try:
        data = request.json or {}
        
        # 1. Validate the Request Body Key Names / Token
        token = data.get("token") or data.get("sb_token") or data.get("access_token")
        
        if token:
            # Authenticate via Supabase access token (token exchange flow)
            sb_user_resp = supabase.auth.get_user(token)
            user = getattr(sb_user_resp, 'user', None)
            email = getattr(user, 'email', None) if user else None
            
            if not email:
                raise ValueError("Invalid token or missing email in token")
                
            db = get_db()
            row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
            metadata = getattr(user, 'user_metadata', {}) or {}
            name = metadata.get("name") or email.split("@")[0]
            role, org_id, center_id = resolve_user_profile(email, metadata)
            
            if not row:
                # Synchronize user locally if not found
                db_url = os.environ.get("DATABASE_URL")
                is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES
                if is_postgres:
                    db.execute("INSERT INTO users (id, name, email, role, organization_id, center_id, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING", (user.id, name, email, role, org_id, center_id, "supabase_auth"))
                else:
                    db.execute("INSERT INTO users (name, email, role, organization_id, center_id, password_hash) VALUES (?, ?, ?, ?, ?, ?)", (name, email, role, org_id, center_id, "supabase_auth"))
                db.commit()
                row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
            elif row and (row["role"] != role or row.get("organization_id") != org_id or row.get("center_id") != center_id):
                # Synchronize local database role if it differs from Supabase Auth metadata
                db.execute("UPDATE users SET role = ?, organization_id = ?, center_id = ? WHERE email = ?", (role, org_id, center_id, email))
                db.commit()
                row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                
            user_payload = {
                "id": row["id"] if row else user.id,
                "name": row["name"] if row else name,
                "email": row["email"] if row else email,
                "role": row["role"] if row else role,
                "organization_id": row["organization_id"] if row else org_id,
                "center_id": row["center_id"] if row else center_id
            }
            
            return jsonify({
                "token": token,
                "user": user_payload
            }), 200
            
        else:
            # Authenticate utilizing credentials (email/password flow)
            email = data.get("email") or data.get("emailAddress") or data.get("username")
            password = data.get("password")
            
            if not email or not password:
                return jsonify({"error": "Missing credentials"}), 400
                
            # Authenticate utilizing the active supabase instance variable
            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            # Ensure proper response structure of supabase.auth.sign_in_with_password()
            session = getattr(auth_response, 'session', None)
            user = getattr(auth_response, 'user', None)
            access_token = session.access_token if session else None
            
            if not access_token:
                raise ValueError("Failed to retrieve access token from authentication response")
                
            db = get_db()
            row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
            metadata = getattr(user, 'user_metadata', {}) or {}
            name = metadata.get("name") or email.split("@")[0]
            role, org_id, center_id = resolve_user_profile(email, metadata)
            
            if not row:
                # Synchronize user locally if not found
                db_url = os.environ.get("DATABASE_URL")
                is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES
                if is_postgres:
                    db.execute("INSERT INTO users (id, name, email, role, organization_id, center_id, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING", (user.id, name, email, role, org_id, center_id, "supabase_auth"))
                else:
                    db.execute("INSERT INTO users (name, email, role, organization_id, center_id, password_hash) VALUES (?, ?, ?, ?, ?, ?)", (name, email, role, org_id, center_id, "supabase_auth"))
                db.commit()
                row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
            elif row and (row["role"] != role or row.get("organization_id") != org_id or row.get("center_id") != center_id):
                # Synchronize local database role if it differs from Supabase Auth metadata
                db.execute("UPDATE users SET role = ?, organization_id = ?, center_id = ? WHERE email = ?", (role, org_id, center_id, email))
                db.commit()
                row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                
            user_payload = {
                "id": row["id"] if row else user.id,
                "name": row["name"] if row else name,
                "email": row["email"] if row else email,
                "role": row["role"] if row else role,
                "organization_id": row["organization_id"] if row else org_id,
                "center_id": row["center_id"] if row else center_id
            }
            
            return jsonify({
                "token": access_token,
                "user": user_payload
            }), 200

            
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        print("====== AUTH GATEWAY CRASH LOG ======")
        print(f"Exception Type: {type(e)}")
        print(f"Exception Details: {str(e)}")
        print(tb_str)
        print("====================================")
        try:
            with open(os.path.join(os.path.dirname(__file__), "debug_logs.txt"), "a", encoding="utf-8") as f:
                f.write(f"\n====== {datetime.now()} ======\n")
                f.write(f"Exception Type: {type(e)}\n")
                f.write(f"Exception Details: {str(e)}\n")
                f.write(tb_str)
                f.write("====================================\n")
        except Exception as log_err:
            print(f"Failed to write to debug_logs.txt: {log_err}")
            
        return jsonify({"error": str(e), "message": "Authentication pipeline failed internally"}), 400

@app.route("/api/debug/logs", methods=["GET"])
def get_debug_logs():
    try:
        log_path = os.path.join(os.path.dirname(__file__), "debug_logs.txt")
        if os.path.exists(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                content = f.read()
            return content, 200, {"Content-Type": "text/plain; charset=utf-8"}
        else:
            return "No debug logs found.", 200
    except Exception as e:
        return f"Error reading logs: {e}", 500

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "goat.db")

@app.route("/api/health", methods=["GET"])
def health_check():
    import traceback
    db_url = os.environ.get("DATABASE_URL")
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    
    db_status = "unknown"
    db_error = None
    db_type = "unknown"
    try:
        db = get_db()
        db.execute("SELECT 1")
        db_status = "connected"
        if "SQLite" in str(type(db)):
            db_type = "sqlite"
        else:
            db_type = "postgres"
    except Exception as e:
        db_status = "failed"
        db_error = str(e) + "\n" + traceback.format_exc()
        
    return jsonify({
        "status": "healthy" if db_status == "connected" else "degraded",
        "has_postgres": HAS_POSTGRES,
        "postgres_import_error": POSTGRES_IMPORT_ERROR,
        "db_type": db_type,
        "db_status": db_status,
        "db_error": db_error,
        "render_env": {
            "GIT_BRANCH": os.environ.get("RENDER_GIT_BRANCH"),
            "GIT_COMMIT": os.environ.get("RENDER_GIT_COMMIT"),
            "SERVICE_ID": os.environ.get("RENDER_SERVICE_ID"),
            "SERVICE_NAME": os.environ.get("RENDER_SERVICE_NAME"),
            "EXTERNAL_URL": os.environ.get("RENDER_EXTERNAL_URL"),
        },
        "env_keys": list(os.environ.keys()),
        "has_db_url": bool(db_url),
        "db_url_length": len(db_url) if db_url else 0,
        "has_supabase_url": bool(supabase_url),
    })


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
HAS_POSTGRES = False
POSTGRES_IMPORT_ERROR = None
try:
    import psycopg2
    import psycopg2.extras
    HAS_POSTGRES = True
except Exception as e:
    import traceback
    POSTGRES_IMPORT_ERROR = str(e) + "\n" + traceback.format_exc()

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
                conn = psycopg2.connect(db_url, connect_timeout=10)
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

def resolve_user_profile(email, metadata):
    # Hardcoded values for default accounts
    # Master accounts have organization_id=None, center_id=None
    if email == "dravenshadowsong@gmail.com":
        return "master_admin", None, None
    if email == "master@goat.com":
        return "master_admin", None, None
    if email == "admin@goat.com":
        return "admin", 1, None
    if email == "facilitator@goat.com":
        return "facilitator", 1, 1
    if email == "mentor@goat.com":
        return "mentor", 1, None
    if email == "student@goat.com":
        return "student", 1, 1
    if email == "parent@goat.com":
        return "parent", 1, 1

    role = "facilitator"
    org_id = None
    center_id = None

    # Check remote Supabase profiles table first
    if supabase_client:
        try:
            res = supabase_client.table("profiles").select("role, is_approved, organization_id, center_id").eq("email", email).execute()
            if res.data:
                profile = res.data[0]
                role_str = profile.get("role")
                is_approved = profile.get("is_approved")
                org_id = profile.get("organization_id")
                center_id = profile.get("center_id")
                if role_str:
                    role_str = str(role_str).lower()
                    if is_approved:
                        role = role_str
                    else:
                        if not role_str.startswith("pending_"):
                            role = "pending_" + role_str
                        else:
                            role = role_str
                return role, org_id, center_id
        except Exception as e:
            print(f"[SUPABASE WARNING] Failed to fetch profile info for {email}: {e}")

    # Fallback/default logic:
    if metadata and isinstance(metadata, dict):
        meta_role = metadata.get("role")
        if meta_role:
            role = str(meta_role).lower()
        org_id = metadata.get("organization_id") or org_id
        center_id = metadata.get("center_id") or center_id

    # Check local database
    try:
        db = get_db()
        row = db.execute("SELECT role, organization_id, center_id FROM users WHERE email = ?", (email,)).fetchone()
        if row:
            if row["role"]:
                role = str(row["role"]).lower()
            if row["organization_id"] is not None:
                org_id = row["organization_id"]
            if row["center_id"] is not None:
                center_id = row["center_id"]
    except Exception as e:
        print(f"[DATABASE WARNING] Failed to fetch existing local profile for {email}: {e}")

    return role, org_id, center_id

def resolve_user_role(email, metadata):
    role, _, _ = resolve_user_profile(email, metadata)
    return role


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

    # Check if this is a Supabase JWT token
    if token.startswith("eyJ") and supabase:
        try:
            sb_user_resp = supabase.auth.get_user(token)
            if sb_user_resp and sb_user_resp.user:
                sb_user = sb_user_resp.user
                email = sb_user.email

                db = get_db()
                row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                metadata = getattr(sb_user, 'user_metadata', {}) or {}
                name = metadata.get("name") or email.split("@")[0]
                role, org_id, center_id = resolve_user_profile(email, metadata)
                
                if row:
                    if row["role"] != role or row.get("organization_id") != org_id or row.get("center_id") != center_id:
                        db.execute("UPDATE users SET role = ?, organization_id = ?, center_id = ? WHERE email = ?", (role, org_id, center_id, email))
                        db.commit()
                        row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                    return dict(row)
                else:
                    db_url = os.environ.get("DATABASE_URL")
                    is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES
                    if is_postgres:
                        db.execute("INSERT INTO users (id, name, email, role, organization_id, center_id, password_hash) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT (id) DO NOTHING", (sb_user.id, name, email, role, org_id, center_id, "supabase_auth"))
                    else:
                        db.execute("INSERT INTO users (name, email, role, organization_id, center_id, password_hash) VALUES (?, ?, ?, ?, ?, ?)", (name, email, role, org_id, center_id, "supabase_auth"))
                    db.commit()
                    row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                    if row:
                        return dict(row)
            else:
                return None
        except Exception as e:
            print(f"[AUTH ERROR] Supabase token verification failed: {e}")
            return None

    # Fallback to local session check
    row = get_db().execute("""
        SELECT u.id, u.name, u.email, u.role, u.organization_id, u.center_id
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

def require_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user, error = require_user()
        if error:
            return error
        return f(*args, **kwargs)
    return decorated_function

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
            conn = psycopg2.connect(db_url, connect_timeout=10)
            cursor = conn.cursor()
            
            schema_path = os.path.join(os.path.dirname(__file__), "db", "postgres_schema.sql")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            
            cursor.execute(schema_sql)
            conn.commit()
            cursor.close()
            
            # Seed data for postgres
            cursor = conn.cursor()
            
            # 1. Seed organizations
            try:
                cursor.execute("SELECT COUNT(*) FROM organizations")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO organizations (id, name) VALUES (1, 'GOAT Labs')")
                    conn.commit()
            except Exception as e:
                print(f"[DATABASE WARNING] Failed to seed organizations on Postgres: {e}")
                conn.rollback()
                
            # 2. Seed centers
            try:
                cursor.execute("SELECT COUNT(*) FROM centers")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO centers (id, name, location, organization_id) VALUES
                        (1, 'Khadar Centre', 'Khadar', 1),
                        (2, 'Okhla Centre', 'Okhla', 1),
                        (3, 'Govindpuri Centre', 'Govindpuri', 1),
                        (4, 'Yamuna Centre', 'Yamuna', 1)
                    """)
                    conn.commit()
            except Exception as e:
                print(f"[DATABASE WARNING] Failed to seed centers on Postgres: {e}")
                conn.rollback()
                
            # 3. Seed users
            try:
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES
                        ('Master Admin', 'master@goat.com', %s, 'master_admin', NULL, NULL),
                        ('Admin Account', 'admin@goat.com', %s, 'admin', 1, NULL),
                        ('Demo Facilitator', 'facilitator@goat.com', %s, 'facilitator', 1, 1),
                        ('Demo Mentor', 'mentor@goat.com', %s, 'mentor', 1, NULL),
                        ('Demo Student', 'student@goat.com', %s, 'student', 1, 1),
                        ('Demo Parent', 'parent@goat.com', %s, 'parent', 1, 1)
                    """, (hash_password("goat123"), hash_password("goat123"), hash_password("goat123"), hash_password("goat123"), hash_password("goat123"), hash_password("goat123")))
                    conn.commit()
            except Exception as e:
                print(f"[DATABASE WARNING] Failed to seed users on Postgres: {e} (Expected on Supabase due to UUID/FK constraints). Skipping.")
                conn.rollback()
            
            # 4. Seed mentors
            try:
                cursor.execute("SELECT COUNT(*) FROM mentors")
                if cursor.fetchone()[0] == 0:
                    cursor.execute("""
                        INSERT INTO mentors (id, name, domain, bio, contact) VALUES
                        (1, 'Anita Sharma',    'creative',       'Art teacher, 12 yrs experience', 'anita@goat.com'),
                        (2, 'Rahul Gupta',     'logical',        'Math tutor, IIT graduate',       'rahul@goat.com'),
                        (3, 'Priya Mehta',     'kinesthetic',    'Dance instructor, Kathak',       'priya@goat.com'),
                        (4, 'Suresh Kumar',    'spatial',        'Carpenter & craft trainer',      'suresh@goat.com'),
                        (5, 'Deepa Nair',      'social',         'Community organiser, 8 yrs',     'deepa@goat.com'),
                        (6, 'Arjun Singh',     'language',       'Theatre director, storyteller',  'arjun@goat.com'),
                        (7, 'Meena Iyer',      'naturalist',     'Botanist, nature educator',      'meena@goat.com'),
                        (8, 'Kavita Bose',     'intrapersonal',  'Counsellor, mindfulness guide',  'kavita@goat.com')
                    """)
                    conn.commit()
            except Exception as e:
                print(f"[DATABASE WARNING] Failed to seed mentors on Postgres: {e}")
                conn.rollback()
                
            # 4. Seed/Sync puzzles
            try:
                for p in DEFAULT_AI_PUZZLES:
                    cursor.execute("""
                        INSERT INTO puzzles (key, type, domain, component, data)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (key) DO UPDATE 
                        SET type = EXCLUDED.type, domain = EXCLUDED.domain, component = EXCLUDED.component, data = EXCLUDED.data
                    """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
                conn.commit()
            except Exception as e:
                print(f"[DATABASE WARNING] Failed to sync puzzles on Postgres: {e}")
                conn.rollback()
            
            # Ensure dravenshadowsong@gmail.com is master_admin in remote Postgres
            try:
                cursor.execute("UPDATE users SET role = 'master_admin' WHERE email = 'dravenshadowsong@gmail.com'")
                conn.commit()
            except Exception as pg_update_err:
                print(f"Failed to update remote Postgres role for dravenshadowsong@gmail.com: {pg_update_err}")
                conn.rollback()
                
            conn.close()
            print("[SUCCESS] PostgreSQL/Supabase initialized successfully!")
        except Exception as e:
            print(f"[DATABASE ERROR] Failed to initialize Postgres: {e}. Falling back to SQLite.")
            
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS organizations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS centers (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
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
            organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
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
            organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
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
            organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
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
            (1, 'Anita Sharma',    'creative',       'Art teacher, 12 yrs experience', 'anita@goat.com'),
            (2, 'Rahul Gupta',     'logical',        'Math tutor, IIT graduate',       'rahul@goat.com'),
            (3, 'Priya Mehta',     'kinesthetic',    'Dance instructor, Kathak',       'priya@goat.com'),
            (4, 'Suresh Kumar',    'spatial',        'Carpenter & craft trainer',      'suresh@goat.com'),
            (5, 'Deepa Nair',      'social',         'Community organiser, 8 yrs',     'deepa@goat.com'),
            (6, 'Arjun Singh',     'language',       'Theatre director, storyteller',  'arjun@goat.com'),
            (7, 'Meena Iyer',      'naturalist',     'Botanist, nature educator',      'meena@goat.com'),
            (8, 'Kavita Bose',     'intrapersonal',  'Counsellor, mindfulness guide',  'kavita@goat.com');
        """)
        
    if db.execute("SELECT COUNT(*) FROM organizations").fetchone()[0] == 0:
        db.execute("INSERT INTO organizations (id, name) VALUES (1, 'GOAT Labs')")

    if db.execute("SELECT COUNT(*) FROM centers").fetchone()[0] == 0:
        db.execute("INSERT INTO centers (id, name, location, organization_id) VALUES (1, 'Khadar Centre', 'Khadar', 1)")
        db.execute("INSERT INTO centers (id, name, location, organization_id) VALUES (2, 'Okhla Centre', 'Okhla', 1)")
        db.execute("INSERT INTO centers (id, name, location, organization_id) VALUES (3, 'Govindpuri Centre', 'Govindpuri', 1)")
        db.execute("INSERT INTO centers (id, name, location, organization_id) VALUES (4, 'Yamuna Centre', 'Yamuna', 1)")

    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.execute("INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES ('Master Admin', 'master@goat.com', ?, 'master_admin', NULL, NULL)", (hash_password("goat123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES ('Admin Account', 'admin@goat.com', ?, 'admin', 1, NULL)", (hash_password("goat123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES ('Demo Facilitator', 'facilitator@goat.com', ?, 'facilitator', 1, 1)", (hash_password("goat123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES ('Demo Mentor', 'mentor@goat.com', ?, 'mentor', 1, NULL)", (hash_password("goat123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES ('Demo Student', 'student@goat.com', ?, 'student', 1, 1)", (hash_password("goat123"),))
        db.execute("INSERT INTO users (name, email, password_hash, role, organization_id, center_id) VALUES ('Demo Parent', 'parent@goat.com', ?, 'parent', 1, 1)", (hash_password("goat123"),))
        
    # Seed/Sync puzzles
    for p in DEFAULT_AI_PUZZLES:
        db.execute("""
            INSERT OR REPLACE INTO puzzles (key, type, domain, component, data)
            VALUES (?, ?, ?, ?, ?)
        """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
            
    # Dynamic SQLite migration to ensure old database versions have all required columns
    try:
        expected_columns = {
            "centers": {
                "organization_id": "INTEGER REFERENCES organizations(id) ON DELETE CASCADE"
            },
            "users": {
                "active": "INTEGER DEFAULT 1",
                "organization_id": "INTEGER REFERENCES organizations(id) ON DELETE SET NULL",
                "center_id": "INTEGER REFERENCES centers(id) ON DELETE SET NULL",
                "student_id": "INTEGER"
            },
            "children": {
                "exp_kinesthetic": "INTEGER DEFAULT 0",
                "exp_creative": "INTEGER DEFAULT 0",
                "exp_logical": "INTEGER DEFAULT 0",
                "exp_spatial": "INTEGER DEFAULT 0",
                "exp_social": "INTEGER DEFAULT 0",
                "exp_language": "INTEGER DEFAULT 0",
                "exp_naturalist": "INTEGER DEFAULT 0",
                "exp_intrapersonal": "INTEGER DEFAULT 0",
                "organization_id": "INTEGER REFERENCES organizations(id) ON DELETE CASCADE",
                "center_id": "INTEGER REFERENCES centers(id) ON DELETE SET NULL"
            },
            "workshops": {
                "organization_id": "INTEGER REFERENCES organizations(id) ON DELETE CASCADE"
            },
            "sessions": {
                "domain_flags": "TEXT",
                "tq_scores": "TEXT",
                "eq_score": "INTEGER",
                "visualizer_score": "INTEGER",
                "personality_data": "TEXT",
                "integrated_score": "TEXT",
                "top_domain": "TEXT",
                "generated_tasks": "TEXT",
                "status": "TEXT DEFAULT 'in_progress'",
                "completed_at": "TEXT"
            }
        }
        for table, cols in expected_columns.items():
            cursor = db.execute(f"PRAGMA table_info({table})")
            existing_cols = {row[1] for row in cursor.fetchall()}
            for col, col_def in cols.items():
                if col not in existing_cols:
                    print(f"[MIGRATION] Adding missing column {col} to table {table}...")
                    db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
    except Exception as migration_err:
        print(f"[MIGRATION WARNING] Failed to migrate local SQLite schema: {migration_err}")

    db.commit()
    db.close()
    
    # Ensure dravenshadowsong@gmail.com is master_admin in local SQLite
    try:
        sqlite_db = sqlite3.connect(DB_PATH)
        sqlite_db.execute("UPDATE users SET role = 'master_admin' WHERE email = 'dravenshadowsong@gmail.com'")
        sqlite_db.commit()
        sqlite_db.close()
    except Exception as local_update_err:
        print(f"Failed to update local SQLite role for dravenshadowsong@gmail.com: {local_update_err}")
        
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
                {"id": 1, "name": "Anita Sharma",    "domain": "creative",       "bio": "Art teacher, 12 yrs experience", "contact": "anita@goat.com"},
                {"id": 2, "name": "Rahul Gupta",     "domain": "logical",        "bio": "Math tutor, IIT graduate",       "contact": "rahul@goat.com"},
                {"id": 3, "name": "Priya Mehta",     "domain": "kinesthetic",    "bio": "Dance instructor, Kathak",       "contact": "priya@goat.com"},
                {"id": 4, "name": "Suresh Kumar",    "domain": "spatial",        "bio": "Carpenter & craft trainer",      "contact": "suresh@goat.com"},
                {"id": 5, "name": "Deepa Nair",      "domain": "social",         "bio": "Community organiser, 8 yrs",     "contact": "deepa@goat.com"},
                {"id": 6, "name": "Arjun Singh",     "domain": "language",       "bio": "Theatre director, storyteller",  "contact": "arjun@goat.com"},
                {"id": 7, "name": "Meena Iyer",      "domain": "naturalist",     "bio": "Botanist, nature educator",      "contact": "meena@goat.com"},
                {"id": 8, "name": "Kavita Bose",     "domain": "intrapersonal",  "bio": "Counsellor, mindfulness guide",  "contact": "kavita@goat.com"}
            ]
            supabase_client.table("mentors").insert(mentors_data).execute()
            
    except Exception as e:
        print(f"[SUPABASE WARNING] Failed to seed static tables on Supabase: {e}")



# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Children
# ═══════════════════════════════════════════════════════════════════════════════

# ROUTES - Auth

# Legacy login route commented out to prevent route conflicts with auth_login_gate
# @app.route("/api/auth/login", methods=["POST"])
# def login():
#     data = request.json or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password") or ""
#     db = get_db()
#     row = db.execute("SELECT * FROM users WHERE email=? AND active=1", (email,)).fetchone()
#     if not row or not check_password(password, row["password_hash"]):
#         return jsonify({"error": "Invalid email or password"}), 401
# 
#     token = secrets.token_urlsafe(32)
#     db.execute("""
#         INSERT INTO auth_sessions (user_id, token, expires_at)
#         VALUES (?, ?, datetime('now', '+12 hours'))
#     """, (row["id"], token))
#     db.commit()
#     return jsonify({
#         "token": token,
#         "user": {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]},
#     })

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

# Legacy login_supabase route commented out to prevent route conflicts with auth_login_gate
# @app.route("/api/auth/login-supabase", methods=["POST"])
# def login_supabase():
#     data = request.json or {}
#     sb_token = data.get("token")
#     if not sb_token:
#         return jsonify({"error": "Token is required"}), 400
#         
#     supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
#     if not supabase_url:
#         return jsonify({"error": "Supabase URL not configured on server"}), 500
#         
#     import urllib.request
#     import urllib.error
#     req_url = f"{supabase_url.rstrip('/')}/auth/v1/user"
#     headers = {
#         "Authorization": f"Bearer {sb_token}",
#         "apikey": os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
#     }
#     req = urllib.request.Request(req_url, headers=headers)
#     try:
#         with urllib.request.urlopen(req) as response:
#             user_data = json.loads(response.read().decode("utf-8"))
#     except urllib.error.HTTPError as e:
#         return jsonify({"error": "Invalid Supabase session"}), 401
#     except Exception as e:
#         return jsonify({"error": f"Failed to connect to Supabase Auth: {e}"}), 500
#         
#     user_id = user_data.get("id")
#     email = user_data.get("email")
#     
#     db = get_db()
#     row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
#     if not row:
#         name = user_data.get("user_metadata", {}).get("name", "New User")
#         role = user_data.get("user_metadata", {}).get("role", "facilitator")
#         db_url = os.environ.get("DATABASE_URL")
#         is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")) and HAS_POSTGRES
#         if is_postgres:
#             db.execute("INSERT INTO users (id, name, email, role) VALUES (?, ?, ?, ?) ON CONFLICT (id) DO NOTHING", (user_id, name, email, role))
#         else:
#             db.execute("INSERT INTO users (name, email, role) VALUES (?, ?, ?)", (name, email, role))
#         db.commit()
#         row = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
#         
#     token = secrets.token_urlsafe(32)
#     db.execute("""
#         INSERT INTO auth_sessions (user_id, token, expires_at)
#         VALUES (?, ?, datetime('now', '+12 hours'))
#     """, (row["id"], token))
#     db.commit()
#     
#     return jsonify({
#         "token": token,
#         "user": {"id": row["id"], "name": row["name"], "email": row["email"], "role": row["role"]}
#     })

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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    if role == "master_admin":
        rows = db.execute("""
            SELECT c.*, cnt.name AS center_name,
                   s.id AS latest_session_id,
                   s.top_domain,
                   s.personality_data,
                   s.tq_scores
            FROM children c
            LEFT JOIN centers cnt ON cnt.id = c.center_id
            LEFT JOIN (
                SELECT s1.id, s1.child_id, s1.top_domain, s1.personality_data, s1.tq_scores
                FROM sessions s1
                INNER JOIN (
                    SELECT child_id, MAX(id) as max_id
                    FROM sessions
                    WHERE status = 'complete'
                    GROUP BY child_id
                ) s2 ON s1.id = s2.max_id
            ) s ON s.child_id = c.id
            ORDER BY c.created_at DESC
        """).fetchall()
    elif role == "admin": # Org Admin
        rows = db.execute("""
            SELECT c.*, cnt.name AS center_name,
                   s.id AS latest_session_id,
                   s.top_domain,
                   s.personality_data,
                   s.tq_scores
            FROM children c
            LEFT JOIN centers cnt ON cnt.id = c.center_id
            LEFT JOIN (
                SELECT s1.id, s1.child_id, s1.top_domain, s1.personality_data, s1.tq_scores
                FROM sessions s1
                INNER JOIN (
                    SELECT child_id, MAX(id) as max_id
                    FROM sessions
                    WHERE status = 'complete'
                    GROUP BY child_id
                ) s2 ON s1.id = s2.max_id
            ) s ON s.child_id = c.id
            WHERE c.organization_id = ?
            ORDER BY c.created_at DESC
        """, (org_id,)).fetchall()
    else: # Facilitator, etc.
        rows = db.execute("""
            SELECT c.*, cnt.name AS center_name,
                   s.id AS latest_session_id,
                   s.top_domain,
                   s.personality_data,
                   s.tq_scores
            FROM children c
            LEFT JOIN centers cnt ON cnt.id = c.center_id
            LEFT JOIN (
                SELECT s1.id, s1.child_id, s1.top_domain, s1.personality_data, s1.tq_scores
                FROM sessions s1
                INNER JOIN (
                    SELECT child_id, MAX(id) as max_id
                    FROM sessions
                    WHERE status = 'complete'
                    GROUP BY child_id
                ) s2 ON s1.id = s2.max_id
            ) s ON s.child_id = c.id
            WHERE c.organization_id = ? AND c.center_id = ?
            ORDER BY c.created_at DESC
        """, (org_id, center_id)).fetchall()
        
    res = []
    for r in rows:
        d = dict(r)
        if d.get("personality_data"):
            try:
                d["personality_data"] = json.loads(d["personality_data"])
            except Exception:
                pass
        if d.get("tq_scores"):
            try:
                d["tq_scores"] = json.loads(d["tq_scores"])
            except Exception:
                pass
        res.append(d)
    return jsonify(res)

@app.route("/api/children", methods=["POST"])
def create_child():
    user = current_user()
    data = request.json or {}
    print("==================================================")
    print(f"DEBUG: create_child called with data: {data}")
    
    if user:
        role = user.get("role")
        user_org_id = user.get("organization_id")
        user_center_id = user.get("center_id")
        
        # Determine organization_id and center_id based on user role
        if role == "master_admin":
            org_id = data.get("organization_id")
            center_id = data.get("center_id")
        elif role == "admin": # Org Admin
            org_id = user_org_id
            center_id = data.get("center_id") # Org Admin can assign to a center in their org
        else: # Facilitator, etc.
            org_id = user_org_id
            center_id = user_center_id
    else:
        # Anonymous registration defaults to Organization 1 and optional center assignment
        org_id = 1
        center_id = data.get("center_id")
        if center_id:
            try:
                center_id = int(center_id)
            except ValueError:
                center_id = None

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
                "exp_intrapersonal": int(data.get("exp_intrapersonal", 0)),
                "organization_id": org_id,
                "center_id": center_id
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
        if not isinstance(db, PostgresConnectionWrapper):
            db.execute("""
                INSERT INTO children
                  (id, name, age, language, school_year, gender,
                   exp_kinesthetic, exp_creative, exp_logical, exp_spatial,
                   exp_social, exp_language, exp_naturalist, exp_intrapersonal,
                   organization_id, center_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                supabase_id,
                data["name"], data["age"], data.get("language", "Hindi"),
                data.get("school_year", ""), data.get("gender", ""),
                data.get("exp_kinesthetic", 0), data.get("exp_creative", 0),
                data.get("exp_logical", 0),    data.get("exp_spatial", 0),
                data.get("exp_social", 0),     data.get("exp_language", 0),
                data.get("exp_naturalist", 0), data.get("exp_intrapersonal", 0),
                org_id, center_id
            ))
            db.commit()
        else:
            print("DEBUG: Postgres connection active. Skipping redundant local insert as Supabase client has already inserted into the shared Postgres instance.")
        child_id = supabase_id
    else:
        cur = db.execute("""
            INSERT INTO children
              (name, age, language, school_year, gender,
               exp_kinesthetic, exp_creative, exp_logical, exp_spatial,
               exp_social, exp_language, exp_naturalist, exp_intrapersonal,
               organization_id, center_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["name"], data["age"], data.get("language", "Hindi"),
            data.get("school_year", ""), data.get("gender", ""),
            data.get("exp_kinesthetic", 0), data.get("exp_creative", 0),
            data.get("exp_logical", 0),    data.get("exp_spatial", 0),
            data.get("exp_social", 0),     data.get("exp_language", 0),
            data.get("exp_naturalist", 0), data.get("exp_intrapersonal", 0),
            org_id, center_id
        ))
        db.commit()
        child_id = cur.lastrowid
        
    return jsonify({"id": child_id}), 201

@app.route("/api/children/<int:cid>", methods=["GET"])
def get_child(cid):
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    row = db.execute("""
        SELECT c.*, cnt.name AS center_name
        FROM children c
        LEFT JOIN centers cnt ON cnt.id = c.center_id
        WHERE c.id = ?
    """, (cid,)).fetchone()
    if not row: return jsonify({"error": "Not found"}), 404
    
    child_dict = dict(row)
    if role != "master_admin":
        if child_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child_dict.get("center_id") is not None and child_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
        # Auto-assign center if currently unassigned and accessed by a facilitator
        if role != "admin" and child_dict.get("center_id") is None and center_id is not None:
            print(f"DEBUG: Auto-assigning unassigned child {cid} to center {center_id} on child profile fetch")
            db.execute("UPDATE children SET center_id = ? WHERE id = ?", (center_id, cid))
            db.commit()
            if supabase_client:
                try:
                    supabase_client.table("children").update({"center_id": center_id}).eq("id", cid).execute()
                except Exception as e:
                    print(f"DEBUG: Exception auto-assigning child center on profile fetch: {e}")
            child_dict["center_id"] = center_id
            
    return jsonify(child_dict)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Sessions
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/sessions", methods=["POST"])
def create_session():
    user = current_user()
    data = request.json or {}
    child_id = data.get("child_id")
    print("==================================================")
    print(f"DEBUG: create_session called with data: {data}")
    
    # Check if the child exists and is within user's scope
    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    child_dict = dict(child)
    if user:
        role = user.get("role")
        org_id = user.get("organization_id")
        center_id = user.get("center_id")
        
        if role != "master_admin":
            if child_dict.get("organization_id") != org_id:
                return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
            if role != "admin" and child_dict.get("center_id") is not None and child_dict.get("center_id") != center_id:
                return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
            # Auto-assign center if currently unassigned and accessed by a facilitator
            if role != "admin" and child_dict.get("center_id") is None and center_id is not None:
                print(f"DEBUG: Auto-assigning unassigned child {child_id} to center {center_id}")
                db.execute("UPDATE children SET center_id = ? WHERE id = ?", (center_id, child_id))
                db.commit()
                if supabase_client:
                    try:
                        supabase_client.table("children").update({"center_id": center_id}).eq("id", child_id).execute()
                    except Exception as e:
                        print(f"DEBUG: Exception auto-assigning child center on session creation: {e}")
                child_dict["center_id"] = center_id
            
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
            
    if supabase_id is not None:
        if not isinstance(db, PostgresConnectionWrapper):
            db.execute(
                "INSERT INTO sessions (id, child_id, phase) VALUES (?,?,?)",
                (supabase_id, child_id, "discovery")
            )
            db.commit()
        else:
            print("DEBUG: Postgres connection active. Skipping redundant local session insert as Supabase client has already inserted.")
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
    user = current_user()
    
    db = get_db()
    row = db.execute("SELECT s.*, c.organization_id, c.center_id FROM sessions s JOIN children c ON s.child_id = c.id WHERE s.id=?", (sid,)).fetchone()
    if not row: return jsonify({"error": "Not found"}), 404
    
    row_dict = dict(row)
    if user:
        role = user.get("role")
        org_id = user.get("organization_id")
        center_id = user.get("center_id")
        
        if role != "master_admin":
            if row_dict.get("organization_id") != org_id:
                return jsonify({"error": "Forbidden: Session belongs to another organization"}), 403
            if role != "admin" and row_dict.get("center_id") is not None and row_dict.get("center_id") != center_id:
                return jsonify({"error": "Forbidden: Session belongs to another center"}), 403
                
            # Auto-assign/claim center if currently unassigned and accessed by a facilitator
            if role != "admin" and row_dict.get("center_id") is None and center_id is not None:
                child_id = row_dict.get("child_id")
                print(f"DEBUG: Auto-assigning unassigned child {child_id} to center {center_id} on session load")
                db.execute("UPDATE children SET center_id = ? WHERE id = ?", (center_id, child_id))
                db.commit()
                if supabase_client:
                    try:
                        supabase_client.table("children").update({"center_id": center_id}).eq("id", child_id).execute()
                    except Exception as e:
                        print(f"DEBUG: Exception auto-assigning child center on session fetch: {e}")
                row_dict["center_id"] = center_id
            
    return jsonify(row_dict)


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
        "title": {"English": "The Project Deadline", "Hindi": "The Project Deadline"},
        "prompt": {
            "English": "Your team has 10 minutes left to submit a project. The poster looks great, but one teammate is upset because the group forgot to include their drawing. The other teammates want to submit immediately to win. What do you do?",
            "Hindi": "Your team has 10 minutes left to submit a project. The poster looks great, but one teammate is upset because the group forgot to include their drawing. The other teammates want to submit immediately to win. What do you do?"
        },
        "options": [
            {"label": {"English": "Submit the project now to ensure the team wins, then promise the teammate to highlight their drawing during the presentation.", "Hindi": "Submit the project now to ensure the team wins, then promise the teammate to highlight their drawing during the presentation."}, "value": 4},
            {"label": {"English": "Delay the submission to glue the drawing on, even if it means missing the absolute deadline, because team unity is more important.", "Hindi": "Delay the submission to glue the drawing on, even if it means missing the absolute deadline, because team unity is more important."}, "value": 4},
            {"label": {"English": "Find a quick, creative compromise, like taping the drawing to the back of the poster as an 'Appendix' to save time.", "Hindi": "Find a quick, creative compromise, like taping the drawing to the back of the poster as an 'Appendix' to save time."}, "value": 4},
            {"label": {"English": "Do nothing and let the other teammates decide.", "Hindi": "Do nothing and let the other teammates decide."}, "value": 1}
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
        "key": "naturalist_weather_pattern",
        "type": "choice",
        "domain": "naturalist",
        "component": "pattern_in_nature",
        "title": {"English": "The Rain Clouds", "Hindi": "बारिश के बादल"},
        "prompt": {
            "English": "You are playing outdoors and notice the wind suddenly blowing cold, swallows flying low, and the sky turning dark grey. What is nature telling you?",
            "Hindi": "आप बाहर खेल रहे हैं और अचानक ठंडी हवा चलने लगती है, चिड़ियाँ नीचे उड़ने लगती हैं, और आसमान गहरा भूरा हो जाता है। प्रकृति आपको क्या बता रही है?"
        },
        "options": [
            {"label": {"English": "A heavy rain shower is coming very soon", "Hindi": "बहुत जल्द तेज़ बारिश होने वाली है"}, "value": 4},
            {"label": {"English": "The sun is going to shine brighter", "Hindi": "सूरज और तेज़ चमकने वाला है"}, "value": 0},
            {"label": {"English": "An earthquake is happening", "Hindi": "भूकंप आ रहा है"}, "value": 0},
            {"label": {"English": "A cold winter night has started", "Hindi": "ठंड की रात शुरू हो गई है"}, "value": 1}
        ],
        "metric": "judgement"
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
        "title": {"English": "The Stuck Kite", "Hindi": "The Stuck Kite"},
        "prompt": {
            "English": "You spent two days making a beautiful paper kite, but on its first flight it gets stuck high in a thorny tree. You cannot reach it. What do you do?",
            "Hindi": "You spent two days making a beautiful paper kite, but on its first flight it gets stuck high in a thorny tree. You cannot reach it. What do you do?"
        },
        "options": [
            {"label": {"English": "Accept that it's gone for now, and start designing a new, improved paper kite using what you learned.", "Hindi": "Accept that it's gone for now, and start designing a new, improved paper kite using what you learned."}, "value": 4},
            {"label": {"English": "Go find a helper or a long tool to try retrieving it, even if it might take a long time and rip the paper.", "Hindi": "Go find a helper or a long tool to try retrieving it, even if it might take a long time and rip the paper."}, "value": 4},
            {"label": {"English": "Ask friends for ideas on how to build a simple pulley or tool to hook the string.", "Hindi": "Ask friends for ideas on how to build a simple pulley or tool to hook the string."}, "value": 4},
            {"label": {"English": "Leave the park feeling angry and give up on flying kites altogether.", "Hindi": "Leave the park feeling angry and give up on flying kites altogether."}, "value": 1}
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

_cached_puzzles = None

def load_puzzles_from_db():
    global _cached_puzzles
    if _cached_puzzles is not None:
        return _cached_puzzles
    try:
        db = get_db()
        rows = db.execute("SELECT data FROM puzzles").fetchall()
        puzzles = []
        for r in rows:
            try:
                puzzles.append(json.loads(r["data"]))
            except Exception:
                pass
        if puzzles:
            _cached_puzzles = puzzles
            return puzzles
        return DEFAULT_AI_PUZZLES
    except Exception:
        return DEFAULT_AI_PUZZLES

LOCAL_PRIMARY_OVERRIDES = {
    "logical_pattern_matrix": {
        "title": {"English": "The Magic Lock", "Hindi": "जादू की संख्या"},
        "prompt": {
            "English": "Add numbers to open the lock. The bottom row has 3 and 5 (= 8). Next are 5 and 9 (= 14). What belongs at the top? (3+5=8, 5+9=14, 8+14=?)",
            "Hindi": "ताला खोलने के लिए संख्याओं को जोड़ें। सबसे नीचे 3 और 5 हैं, जो 8 बनते हैं। उनके बगल में 5 और 9 हैं, जो 14 बनते हैं। सबसे ऊपर क्या आएगा? (3+5=8, 5+9=14, 8+14=?)"
        }
    },
    "logical_riddle": {
        "title": {"English": "The Leg Code", "Hindi": "पैरों का खेल"},
        "prompt": {
            "English": "A cat is 4, a spider is 8, and an ant is 6. What number represents a snake? 🐍",
            "Hindi": "बिल्ली 4 है, मकड़ी 8 है, चींटी 6 है। सांप का नंबर क्या होगा? 🐍"
        }
    },
    "spatial_rotation": {
        "prompt": {
            "English": "A star pointer turns: first UP ↑, then RIGHT →, then DOWN ↓. Where will it point next?",
            "Hindi": "तारे की सुई घूमती है: पहले ऊपर इशारा करती है ↑, फिर दाएं →, फिर नीचे ↓। आगे कहाँ इशारा करेगी?"
        }
    },
    "spatial_perspective": {
        "title": {"English": "Shadow Match", "Hindi": "परछाई का खेल"},
        "prompt": {
            "English": "A T-shaped toy has light shining from the LEFT. What shape of shadow does it make on the wall?",
            "Hindi": "एक 'T' आकार के खिलौने पर बाईं (LEFT) ओर से टॉर्च की रोशनी पड़ने पर दीवार पर कैसी छाया बनेगी?"
        }
    },
    "creative_uses": {
        "prompt": {
            "English": "Imagine gravity pulls you SIDEWAYS at school instead of down! 😮 Write 3 funny things that would happen!",
            "Hindi": "सोचें कि आपके स्कूल में गुरुत्वाकर्षण नीचे के बजाय बगल में काम करने लगे! 😮 3 मजेदार चीजें लिखें जो आपके साथ होंगी!"
        }
    },
    "language_story_order": {
        "title": {"English": "Story Order", "Hindi": "कहानी जमाएं"},
        "prompt": {
            "English": "Put these secret agent message pieces in the correct order to tell the exciting escape story!",
            "Hindi": "इन वाक्यों को सही क्रम में लगाएं ताकि एक मजेदार भागने की कहानी बन सके!"
        }
    },
    "language_analogy": {
        "title": {"English": "Word Connection", "Hindi": "शब्दों का मेल"},
        "prompt": {
            "English": "Complete this word connection: A FEATHER is to a BIRD as a SCALE is to...?",
            "Hindi": "शब्दों का संबंध पूरा करें: एक पंख (FEATHER) चिड़िया (BIRD) के लिए है, तो एक शल्क (SCALE) किसके लिए है...?"
        }
    },
    "kinesthetic_motor_planning": {
        "title": {"English": "The Rope Bridge", "Hindi": "रस्सी का पुल"},
        "prompt": {
            "English": "You are on a wobbling rope bridge. Strong wind blows from the right! What is the best way to balance?",
            "Hindi": "आप एक हिलते हुए रस्सी के पुल पर हैं। दाईं ओर से तेज हवा चलती है! सुरक्षित रहने के लिए आप क्या करेंगे?"
        },
        "options": [
            {"label": {"English": "Bend knees, spread arms, and lean slightly right", "Hindi": "घुटनों को मोड़ें, हाथ फैलाएं और थोड़ा दाईं ओर झुकें"}, "value": 4},
            {"label": {"English": "Stand straight and close eyes", "Hindi": "बिल्कुल सीधे खड़े रहें और आंखें बंद करें"}, "value": 0},
            {"label": {"English": "Run fast to the other side", "Hindi": "जितनी तेजी से हो सके दूसरी तरफ दौड़ें"}, "value": 1},
            {"label": {"English": "Sit down and shout for help", "Hindi": "रस्सी के पुल पर बैठ जाएं और मदद के लिए चिल्लाएं"}, "value": 2}
        ]
    },
    "social_response": {
        "title": {"English": "Helping a Teammate", "Hindi": "साथी की मदद"},
        "prompt": {
            "English": "10 minutes left for a group project. A friend is upset because their drawing was left out. What do you do?",
            "Hindi": "प्रोजेक्ट जमा करने में 10 मिनट बचे हैं। एक दोस्त रो रहा है क्योंकि उसका चित्र भूल गए। बाकी जमा करना चाहते हैं। आप क्या करेंगे?"
        },
        "options": [
            {"label": {"English": "Submit now and highlight their drawing later", "Hindi": "प्रोजेक्ट जमा कर दें, फिर प्रेजेंटेशन में दोस्त के चित्र की बात करें"}, "value": 4},
            {"label": {"English": "Delay to add the drawing because friendship matters most", "Hindi": "देर हो जाए तो भी चित्र चिपकाएं क्योंकि दोस्त की खुशी जरूरी है"}, "value": 4},
            {"label": {"English": "Tape the drawing to the back quickly to save time", "Hindi": "चित्र को पोस्टर के पीछे चिपका दें ताकि समय बच सके"}, "value": 4},
            {"label": {"English": "Do nothing and let others decide", "Hindi": "चुप रहें और दूसरों को फैसला करने दें"}, "value": 1}
        ]
    },
    "social_conflict_resolution": {
        "title": {"English": "Playground Argument", "Hindi": "मैदान का झगड़ा"},
        "prompt": {
            "English": "Two friends argue about a football goal. The game stops. How do you help them play again?",
            "Hindi": "फुटबॉल मैच में दो दोस्त गोल को लेकर झगड़ रहे हैं। खेल रुक गया है। आप झगड़ा कैसे सुलझाएंगे?"
        },
        "options": [
            {"label": {"English": "Flip a coin to decide and continue having fun", "Hindi": "सिक्का उछालकर फैसला करें और खेल जारी रखें"}, "value": 4},
            {"label": {"English": "Shout louder than them to make them stop", "Hindi": "उन दोनों से भी ज़्यादा ज़ोर से चिल्लाएँ ताकि वे चुप हो जाएँ"}, "value": 0},
            {"label": {"English": "Take the ball and walk home", "Hindi": "फुटबॉल लेकर अपने घर चले जाएं"}, "value": 1},
            {"label": {"English": "Blame one friend to end it quickly", "Hindi": "बहस को जल्दी खत्म करने के लिए तुरंत एक सहपाठी को दोषी ठहराएं"}, "value": 0}
        ]
    },
    "naturalist_weather_pattern": {
        "prompt": {
            "English": "Cold wind blows, birds fly low, and the sky turns dark grey. What is nature telling you?",
            "Hindi": "अचानक ठंडी हवा चलने लगती है, पक्षी नीचे उड़ते हैं और आसमान काला हो जाता है। प्रकृति क्या बता रही है?"
        },
        "options": [
            {"label": {"English": "Heavy rain is coming soon", "Hindi": "बहुत जल्द तेज बारिश होने वाली है"}, "value": 4},
            {"label": {"English": "The sun will shine brighter", "Hindi": "सूरज और तेज चमकेगा"}, "value": 0},
            {"label": {"English": "An earthquake is coming", "Hindi": "भूकंप आने वाला है"}, "value": 0},
            {"label": {"English": "A cold winter night has started", "Hindi": "ठंड की रात शुरू हो गई है"}, "value": 1}
        ]
    },
    "naturalist_wind_disperse": {
        "title": {"English": "Butterfly Garden", "Hindi": "तितलियों का बगीचा"},
        "prompt": {
            "English": "You want to attract butterflies to your garden. What is the best thing to do?",
            "Hindi": "आप अपने बगीचे में सुंदर तितलियों को बुलाना चाहते हैं। कौन सा काम सबसे अच्छा होगा?"
        },
        "options": [
            {"label": {"English": "Plant sweet flowers and keep water nearby", "Hindi": "मीठे फूलों के पौधे लगाएं और उथले बर्तन में पानी रखें"}, "value": 4},
            {"label": {"English": "Spray insect spray", "Hindi": "पौधों से दूसरे कीड़ों को दूर रखने के लिए तेज़ कीटनाशक का छिड़काव करें"}, "value": 0},
            {"label": {"English": "Cover flowers with plastic bags", "Hindi": "सभी फूलों को प्लास्टिक की शीट से ढक दें"}, "value": 0},
            {"label": {"English": "Catch butterflies elsewhere and release them", "Hindi": "दूसरे पार्कों से तितलियों को पकड़ें और उन्हें अपने बगीचे में छोड़ दें"}, "value": 1}
        ]
    },
    "intrapersonal_reflection": {
        "title": {"English": "Hard Work", "Hindi": "कठिन काम"},
        "prompt": {
            "English": "When something is hard, do you tell yourself you can do it with practice?",
            "Hindi": "जब आप किसी बहुत कठिन चुनौती का सामना करते हैं, तो क्या आप खुद से कहते हैं कि अभ्यास करने से आप इसमें बेहतर हो सकते हैं?"
        },
        "low": {"English": "No, I get discouraged", "Hindi": "नहीं, मैं हिम्मत हार जाता हूँ"},
        "high": {"English": "Yes, I love to learn!", "Hindi": "हाँ, मुझे सीखना पसंद है!"}
    },
    "intrapersonal_frustration": {
        "title": {"English": "The Stuck Kite", "Hindi": "फंसी पतंग"},
        "prompt": {
            "English": "Your handmade kite gets stuck in a tree. You cannot reach it. What do you do?",
            "Hindi": "आपकी बनाई पतंग पेड़ पर फंस गई है। आप वहां तक नहीं पहुंच सकते। आप क्या करेंगे?"
        },
        "options": [
            {"label": {"English": "Accept it and design a new, better kite", "Hindi": "मान लें कि वह गई, और नई पतंग बनाने की सोचें"}, "value": 4},
            {"label": {"English": "Find a long stick to try to get it down", "Hindi": "एक लंबा डंडा ढूंढकर उसे निकालने की कोशिश करें"}, "value": 4},
            {"label": {"English": "Ask friends for ideas to build a hook tool", "Hindi": "दोस्तों से कहें कि धागा खींचने की मशीन बनाएं"}, "value": 4},
            {"label": {"English": "Go home angry and give up entirely", "Hindi": "गुस्सा होकर घर चले जाएं और पतंग उड़ाना छोड़ दें"}, "value": 1}
        ]
    },
    "deep_discovery_flow": {
        "prompt": {
            "English": "Tell us about a game or drawing that makes you forget about lunchtime! 🎨 What are you doing and why is it so much fun?",
            "Hindi": "हमें किसी ऐसे खेल या चित्रकारी के बारे में बताएं जिसमें आप दोपहर के खाने का समय भी भूल जाते हैं! 🎨 आप क्या कर रहे होते हैं और यह इतना मजेदार क्यों है?"
        }
    },
    "deep_discovery_pride": {
        "prompt": {
            "English": "What is one thing you built or made that you love showing to everyone? 🌟 Describe what you did.",
            "Hindi": "आपने कौन सी एक ऐसी चीज़ बनाई है जो आप सबको दिखाना चाहते हैं? 🌟 बताएं कि आपने उसे कैसे बनाया।"
        }
    },
    "deep_discovery_curiosity": {
        "prompt": {
            "English": "If you could spend a whole day learning anything you want (like magic, space, or building robots), what would it be?",
            "Hindi": "यदि आप अपनी पसंद की कोई भी चीज़ सीखने (जैसे जादू, अंतरिक्ष, या रोबोट बनाना) में एक पूरा दिन बिता सकते हैं, तो आप क्या चुनेंगे?"
        }
    },
    "deep_discovery_vision": {
        "prompt": {
            "English": "If you had a magic wand to fix one big problem in your school or village, what would you fix first?",
            "Hindi": "यदि आपके पास अपने स्कूल या गाँव की किसी एक बड़ी समस्या को ठीक करने के लिए एक जादुई छड़ी हो, तो आप पहले क्या ठीक करेंगे?"
        }
    }
}

LOCAL_ADVANCED_OVERRIDES = {
    "logical_pattern_matrix": {
        "title": {"English": "The Numerical Matrix Crypt", "Hindi": "संख्यात्मक मैट्रिक्स"},
        "prompt": {
            "English": "Analyze the sequence hierarchy in a numerical matrix where base inputs of 3 and 5 sum to 8, adjacent inputs 5 and 9 sum to 14, and mid-tier outputs sum to the apex. Calculate the missing value at the apex of the structure. (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)",
            "Hindi": "संख्यात्मक मैट्रिक्स में अनुक्रम पदानुक्रम का विश्लेषण करें जहां 3 और 5 का योग 8 है, 5 और 9 का योग 14 है, और मध्य-स्तरीय योग शीर्ष की ओर बढ़ते हैं। शीर्ष पर अज्ञात मान की गणना करें। (3 + 5 = 8; 5 + 9 = 14; 8 + 14 = ?)"
        }
    },
    "logical_riddle": {
        "title": {"English": "The Taxonomic Leg-Count Cipher", "Hindi": "वर्गीकरण कोड"},
        "prompt": {
            "English": "An abstract cipher maps biological entities to indices based on their appendages: Feline represents 4, Arachnid represents 8, Formicidae represents 6. Determine the numerical value mapping to Serpentes.",
            "Hindi": "एक अमूर्त सिफर जीवों को उनके अंगों के आधार पर अनुक्रमित करता है: बिल्ली (Feline) 4 को दर्शाती है, मकड़ी (Arachnid) 8 को, और चींटी (Formicidae) 6 को। सर्प (Serpentes) के लिए सही संख्या निर्धारित करें।"
        }
    },
    "spatial_rotation": {
        "prompt": {
            "English": "A vector indicator on a coordinate system rotates sequentially: pointing 90 degrees (North), 0 degrees (East), then 270 degrees (South). Compute the next heading in the cycle.",
            "Hindi": "एक समन्वय प्रणाली (coordinate system) में एक वेक्टर संकेतक क्रमिक रूप से घूमता है: पहले 90 डिग्री (उत्तर), फिर 0 डिग्री (पूर्व), और फिर 270 डिग्री (दक्षिण)। चक्र में अगले हेडिंग की गणना करें।"
        }
    },
    "spatial_perspective": {
        "title": {"English": "Orthographic Projection Shadow", "Hindi": "ऑर्थोग्राफिक प्रोजेक्शन शैडो"},
        "prompt": {
            "English": "A three-dimensional planar T-shaped structure is cast under a light source from the direct lateral left axis. What two-dimensional orthographic silhouette is projected onto the wall?",
            "Hindi": "एक त्रि-आयामी (3D) समतलीय T-आकार की संरचना को बाईं ओर (lateral left) से प्रकाश स्रोत के नीचे रखा गया है। दीवार पर कौन सी द्वि-आयामी (2D) ऑर्थोग्राफिक परछाई दिखाई देगी?"
        }
    },
    "creative_uses": {
        "prompt": {
            "English": "Hypothesize a scenario where gravity shifts to operate along the horizontal lateral axis rather than the vertical pull. Propose 3 distinct, highly divergent consequences of this physical anomaly on daily routines.",
            "Hindi": "एक ऐसी स्थिति की परिकल्पना करें जहां गुरुत्वाकर्षण ऊर्ज्वाधर (vertical) खिंचाव के बजाय क्षैतिज (horizontal lateral) अक्ष पर काम करना शुरू कर देता है। दैनिक जीवन पर इस भौतिक विसंगति के 3 बिल्कुल अलग परिणामों का प्रस्ताव दें।"
        }
    },
    "language_story_order": {
        "title": {"English": "Narrative Reconstruction Sequence", "Hindi": "कथा पुनर्निर्माण क्रम"},
        "prompt": {
            "English": "Reconstruct the chronological order of these compound narrative segments to establish a coherent, logically flowing adventure sequence.",
            "Hindi": "एक सुसंगत और तार्किक कहानी स्थापित करने के लिए इन मिश्रित कथा खंडों के कालानुक्रमिक (chronological) क्रम को पुनर्गठित करें।"
        }
    },
    "language_analogy": {
        "title": {"English": "Semantic Analogy Bridge", "Hindi": "सिमेंटिक सादृश्य पुल"},
        "prompt": {
            "English": "Determine the semantic correlation to complete the analogical bridge: FEATHER is to BIRD as SCALE is to...?",
            "Hindi": "सादृश्य संबंध को पूरा करने के लिए सही अर्थपूर्ण शब्द का चयन करें: पंख (FEATHER) का जो संबंध पक्षी (BIRD) से है, वही शल्क (SCALE) का किससे है...?"
        }
    },
    "kinesthetic_motor_planning": {
        "title": {"English": "Biomechanical Stabilization", "Hindi": "बायोमैकेनिकल स्थिरता"},
        "prompt": {
            "English": "While traversing an unstable, high rope bridge, you encounter a sudden, high-velocity wind force from the right lateral axis. What physical stabilization strategy best maintains equilibrium?",
            "Hindi": "एक अस्थिर, ऊंचे रस्सी के पुल को पार करते समय, आपको दाईं ओर से अचानक तेज गति से हवा के झोंके का सामना करना पड़ता है। संतुलन बनाए रखने के लिए सबसे प्रभावी शारीरिक स्थिरीकरण (stabilization) रणनीति क्या है?"
        },
        "options": [
            {"label": {"English": "Lower your center of gravity by flexing knees, extend arms for counterbalance, and lean slightly into the wind", "Hindi": "घुटनों को मोड़कर अपने गुरुत्वाकर्षण केंद्र को कम करें, संतुलन के लिए हाथ फैलाएं, और थोड़ा दाईं ओर (हवा की तरफ) झुकें"}, "value": 4},
            {"label": {"English": "Align body posture fully vertical, close eyes, and stiffen muscle groups", "Hindi": "शरीर की मुद्रा को पूरी तरह से सीधा संरेखित करें, आंखें बंद करें और अपनी मांसपेशियों को कड़ा करें"}, "value": 0},
            {"label": {"English": "Increase linear velocity to minimize exposure time on the bridge", "Hindi": "पुल पर समय कम करने के लिए जितनी जल्दी हो सके दौड़ें"}, "value": 1},
            {"label": {"English": "Decline posture to seated, minimizing wind profile, and signal for external assistance", "Hindi": "हवा के प्रभाव को कम करने के लिए पुल पर बैठ जाएं और बाहरी सहायता का संकेत दें"}, "value": 2}
        ]
    },
    "social_response": {
        "title": {"English": "Collaborative Milestone Conflict", "Hindi": "सहयोगात्मक कार्य संघर्ष"},
        "prompt": {
            "English": "Your team faces an imminent 10-minute project submission deadline. The display is functional, but a teammate is distressed because their contributions were omitted. Other members insist on immediate submission. How do you resolve this?",
            "Hindi": "आपकी टीम के पास प्रोजेक्ट जमा करने के लिए केवल 10 मिनट बचे हैं। प्रोजेक्ट तैयार है, लेकिन एक टीम का सदस्य परेशान है क्योंकि उसका काम शामिल नहीं किया गया है। अन्य सदस्य तुरंत जमा करने पर जोर दे रहे हैं। आप इसे कैसे हल करेंगे?"
        },
        "options": [
            {"label": {"English": "Submit immediately to secure victory, promising to emphasize their role during the oral presentation", "Hindi": "जीत सुनिश्चित करने के लिए तुरंत जमा करें, और मौखिक प्रस्तुति के दौरान उनकी भूमिका पर प्रकाश डालने का वादा करें"}, "value": 4},
            {"label": {"English": "Delay submission to integrate their contribution, prioritizing group cohesion over strict adherence to deadlines", "Hindi": "उनके योगदान को शामिल करने के लिए जमा करने में देरी करें, समय सीमा के बजाय समूह एकता को प्राथमिकता दें"}, "value": 4},
            {"label": {"English": "Execute a rapid compromise, attaching the drawing to the reverse side as a visual appendix to satisfy both interests", "Hindi": "एक त्वरित समझौता खोजें, चित्र को पोस्टर के पीछे 'परिशिष्ट' (Appendix) के रूप में चिपका दें ताकि समय बच सके"}, "value": 4},
            {"label": {"English": "Maintain neutrality and defer the final decision to the collective group vote", "Hindi": "तटस्थ रहें और अंतिम निर्णय को सामूहिक समूह वोट पर छोड़ दें"}, "value": 1}
        ]
    },
    "social_conflict_resolution": {
        "title": {"English": "Peer Dispute Resolution", "Hindi": "सहकर्मी विवाद समाधान"},
        "prompt": {
            "English": "During a competitive activity, an intense dispute arises between two peers regarding whether a scoring event occurred. Tensions escalate and progress halts. How do you intervene?",
            "Hindi": "एक प्रतिस्पर्धी गतिविधि के दौरान, दो सहपाठियों के बीच स्कोरिंग को लेकर तीव्र विवाद उत्पन्न हो जाता है। तनाव बढ़ता है और खेल रुक जाता है। आप कैसे हस्तक्षेप करेंगे?"
        },
        "options": [
            {"label": {"English": "Implement a randomized determination (e.g. coin flip) to restore activity, emphasizing that mutual enjoyment supersedes the score", "Hindi": "गतिविधि को फिर से शुरू करने के लिए एक यादृच्छिक तरीका (जैसे सिक्का उछालना) अपनाएं, और यादिलाएं कि आपसी मज़ा जीत से बड़ा है"}, "value": 4},
            {"label": {"English": "Raise your vocal volume to command attention and demand compliance", "Hindi": "उनका ध्यान आकर्षित करने के लिए अपनी आवाज़ उठाएं और शांत होने की मांग करें"}, "value": 0},
            {"label": {"English": "Withdraw from the group and remove the central equipment to end the activity", "Hindi": "गतिविधि को समाप्त करने के लिए समूह से हट जाएं और खेल का मुख्य सामान अपने साथ ले जाएं"}, "value": 1},
            {"label": {"English": "Assign fault immediately to one individual to expedite resolution", "Hindi": "विवाद को जल्दी सुलझाने के लिए तुरंत एक व्यक्ति को दोषी ठहराएं"}, "value": 0}
        ]
    },
    "naturalist_weather_pattern": {
        "prompt": {
            "English": "You observe a sudden decrease in air temperature, low-altitude avian flight paths, and dense cumulonimbus cloud formations. What meteorological transition is indicated?",
            "Hindi": "आप हवा के तापमान में अचानक गिरावट, पक्षियों की कम ऊंचाई पर उड़ान, और आसमान में घने बादलों के निर्माण को देखते हैं। यह कौन सा मौसमी परिवर्तन दर्शाता है?"
        },
        "options": [
            {"label": {"English": "An imminent heavy precipitation event", "Hindi": "बहुत जल्द होने वाली भारी वर्षा (precipitation)"}, "value": 4},
            {"label": {"English": "Increased solar radiation and clearing conditions", "Hindi": "सूरज का अधिक चमकना और आसमान साफ होना"}, "value": 0},
            {"label": {"English": "Seismic instability", "Hindi": "भूकंपीय अस्थिरता"}, "value": 0},
            {"label": {"English": "Onset of a cold anticyclonic front", "Hindi": "शीत हवा के फ्रंट (cold anticyclonic front) की शुरुआत"}, "value": 1}
        ]
    },
    "naturalist_wind_disperse": {
        "title": {"English": "Ecological Restoration", "Hindi": "पारिस्थितिकी बहाली"},
        "prompt": {
            "English": "You intend to optimize the local insect population in a micro-habitat. Which ecological intervention will support native lepidoptera (butterflies) the most?",
            "Hindi": "आप एक छोटे बगीचे में स्थानीय कीड़ों की आबादी बढ़ाना चाहते हैं। कौन सा उपाय स्थानीय तितलियों (lepidoptera) की सबसे अधिक मदद करेगा?"
        },
        "options": [
            {"label": {"English": "Cultivate native nectar-producing angiosperms and provide accessible hydration stations", "Hindi": "मीठे मकरंद वाले चमकदार स्थानीय फूलों के पौधे लगाएं और पास में उथले बर्तनों में ताजा पानी रखें"}, "value": 4},
            {"label": {"English": "Apply synthetic chemical insecticides to eliminate competing arthropods", "Hindi": "प्रतिस्पर्धी कीड़ों को समाप्त करने के लिए रासायनिक कीटनाशकों का छिड़काव करें"}, "value": 0},
            {"label": {"English": "Enclose the flora fully in protective polyethylene sheets to prevent contamination", "Hindi": "प्रदूषण से बचाने के लिए पौधों को पूरी तरह से पॉलीथीन शीट से ढक दें"}, "value": 0},
            {"label": {"English": "Introduce non-native species captured from distant ecosystems", "Hindi": "दूर के पारिस्थितिकी तंत्र (ecosystems) से पकड़ी गई गैर-स्थानीय प्रजातियों को शामिल करें"}, "value": 1}
        ]
    },
    "intrapersonal_reflection": {
        "title": {"English": "Cognitive Agility & Growth", "Hindi": "संज्ञानात्मक विकास"},
        "prompt": {
            "English": "When confronted with highly challenging cognitive tasks, do you maintain that your abilities in this domain are malleable and improve with systematic effort?",
            "Hindi": "जब आपका सामना किसी कठिन चुनौती से होता है, तो क्या आप मानते हैं कि अभ्यास और योजनाबद्ध प्रयास के माध्यम से आपकी क्षमताएं विकसित हो सकती हैं?"
        },
        "low": {"English": "No, I believe my capacity is fixed and feel discouraged", "Hindi": "नहीं, मेरा मानना है कि मेरी क्षमताएं निश्चित हैं और मैं हतोत्साहित महसूस करता हूँ"},
        "high": {"English": "Yes, I view challenges as opportunities for skill acquisition", "Hindi": "हाँ, मैं चुनौतियों को नए कौशल सीखने के अवसर के रूप में देखता हूँ"}
    },
    "intrapersonal_frustration": {
        "title": {"English": "Resilience Strategy", "Hindi": "लचीलापन रणनीति"},
        "prompt": {
            "English": "You spent significant effort constructing a complex device, but on its initial test it becomes trapped in an inaccessible location. How do you respond?",
            "Hindi": "आपने एक जटिल उपकरण के निर्माण में काफी समय बिताया, लेकिन परीक्षण के दौरान वह एक दुर्गम स्थान पर फंस गया। आपकी प्रतिक्रिया क्या होगी?"
        },
        "options": [
            {"label": {"English": "Acknowledge the loss, analyze the design failures, and initiate construction of an optimized version", "Hindi": "नुकसान को स्वीकार करें, डिजाइन की विफलताओं का विश्लेषण करें और एक बेहतर संस्करण का निर्माण शुरू करें"}, "value": 4},
            {"label": {"English": "Acquire specialized tools to attempt recovery, accepting the risk of physical damage to the device", "Hindi": "उपकरण को निकालने के लिए विशेष उपकरणों की व्यवस्था करें, भले ही इसमें समय लगे और उपकरण क्षतिग्रस्त हो"}, "value": 4},
            {"label": {"English": "Collaborate with peers to engineer a mechanical extraction or pulley apparatus", "Hindi": "उपकरण को निकालने के लिए एक सरल यांत्रिक चरखी (pulley) बनाने के लिए दोस्तों से चर्चा करें"}, "value": 4},
            {"label": {"English": "Abandon the project, experiencing frustration, and cease activities in this domain", "Hindi": "क्रोधित होकर परियोजना को छोड़ दें और इस क्षेत्र में काम करना पूरी तरह बंद कर दें"}, "value": 1}
        ]
    },
    "deep_discovery_flow": {
        "prompt": {
            "English": "Tell us about a complex project, design, or research activity that engages you so deeply that you completely lose track of time. Describe your operational focus.",
            "Hindi": "हमें किसी ऐसे जटिल प्रोजेक्ट, डिजाइन, या शोध गतिविधि के बारे में बताएं जिसमें आप समय का ध्यान भूल जाते हैं। अपनी परिचालन एकाग्रता (operational focus) का वर्णन करें।"
        }
    },
    "deep_discovery_pride": {
        "prompt": {
            "English": "Describe a complex creation, engineered solution, or milestone achievement that you are proud of. What specific problems did you solve?",
            "Hindi": "अपनी किसी ऐसी जटिल रचना, इंजीनियरिंग समाधान या महत्वपूर्ण उपलब्धि का वर्णन करें जिस पर आपको गर्व है। आपने किन विशिष्ट समस्याओं का समाधान किया?"
        }
    },
    "deep_discovery_curiosity": {
        "prompt": {
            "English": "If you could spend one year investigating a single scientific field, technology, or creative domain without academic constraints, what would it be and why?",
            "Hindi": "यदि आप बिना किसी शैक्षणिक प्रतिबंध के एक पूरा वर्ष किसी एकल वैज्ञानिक क्षेत्र, तकनीक या रचनात्मक डोमेन की जांच करने में बिता सकते हैं, तो वह क्या होगा और क्यों?"
        }
    },
    "deep_discovery_vision": {
        "prompt": {
            "English": "Identify a systemic challenge in your community, school, or industry. If you were granted resources, how would you design and implement a solution?",
            "Hindi": "अपने स्कूल, समुदाय या उद्योग में एक प्रणालीगत चुनौती (systemic challenge) की पहचान करें। यदि आपको संसाधन दिए जाएं, तो आप समाधान कैसे तैयार और लागू करेंगे?"
        }
    }
}

def get_complexity_level(school_year, age):
    sy = str(school_year or "").lower().strip()
    if any(c in sy for c in ["class 4", "class 5", "class 6", "grade 4", "grade 5", "grade 6"]):
        return "PRIMARY"
    elif any(c in sy for c in ["class 7", "class 8", "grade 7", "grade 8"]):
        return "MIDDLE"
    elif any(c in sy for c in ["class 9", "class 10", "grade 9", "grade 10"]):
        return "SECONDARY"
    elif any(c in sy for c in ["class 11", "class 12", "grade 11", "grade 12"]):
        return "SENIOR"
        
    try:
        a = int(age)
        if a <= 11:
            return "PRIMARY"
        elif a <= 13:
            return "MIDDLE"
        elif a <= 15:
            return "SECONDARY"
        else:
            return "SENIOR"
    except Exception:
        pass
        
    return "MIDDLE"

def adapt_task_locally(task, complexity, language):
    import re
    is_hindi = str(language or "").lower() == "hindi"
    pref_lang = "Hindi" if is_hindi else "English"
    
    adapted = dict(task)
    
    title_val = task.get("title", "")
    if isinstance(title_val, dict):
        title_val = title_val.get(pref_lang) or title_val.get("English", "")
    
    prompt_val = task.get("prompt", "")
    if isinstance(prompt_val, dict):
        prompt_val = prompt_val.get(pref_lang) or prompt_val.get("English", "")
        
    key = task.get("key")
    if complexity == "PRIMARY" and key in LOCAL_PRIMARY_OVERRIDES:
        override = LOCAL_PRIMARY_OVERRIDES[key]
        if "title" in override:
            title_val = override["title"].get(pref_lang) or override["title"].get("English", "")
        if "prompt" in override:
            prompt_val = override["prompt"].get(pref_lang) or override["prompt"].get("English", "")
        if "options" in override and "options" in task:
            new_opts = []
            for i, opt in enumerate(task.get("options", [])):
                if i < len(override["options"]):
                    over_opt = override["options"][i]
                    lbl = over_opt["label"].get(pref_lang) or over_opt["label"].get("English", "")
                    val = opt.get("value", 0) if isinstance(opt, dict) else 0
                    new_opts.append({"label": lbl, "value": val})
                else:
                    new_opts.append(opt)
            adapted["options"] = new_opts
    elif complexity in ["SECONDARY", "SENIOR"] and key in LOCAL_ADVANCED_OVERRIDES:
        override = LOCAL_ADVANCED_OVERRIDES[key]
        if "title" in override:
            title_val = override["title"].get(pref_lang) or override["title"].get("English", "")
        if "prompt" in override:
            prompt_val = override["prompt"].get(pref_lang) or override["prompt"].get("English", "")
        if "options" in override and "options" in task:
            new_opts = []
            for i, opt in enumerate(task.get("options", [])):
                if i < len(override["options"]):
                    over_opt = override["options"][i]
                    lbl = over_opt["label"].get(pref_lang) or over_opt["label"].get("English", "")
                    val = opt.get("value", 0) if isinstance(opt, dict) else 0
                    new_opts.append({"label": lbl, "value": val})
                else:
                    new_opts.append(opt)
            adapted["options"] = new_opts
    else:
        if complexity == "PRIMARY":
            replacements = {
                r"\bmotivation\b": "drive/fun",
                r"\bresilience\b": "strength",
                r"\bmpathy\b": "caring",
                r"\bleadership\b": "group planning",
                r"\breflection\b": "thinking",
                r"\binitiative\b": "first steps",
                r"\bstrategic\b": "careful",
                r"\bperspective\b": "view",
                r"\banalyze\b": "study",
                r"\banalytical\b": "pattern matching"
            }
            for pattern, rep in replacements.items():
                prompt_val = re.sub(pattern, rep, prompt_val, flags=re.IGNORECASE)
                
            if not any(emoji in prompt_val for emoji in ["🎨", "🧩", "🌟", "🏃", "🤝", "🐞", "🧱"]):
                prompt_val += " 🌟"
                
            if "options" in adapted and isinstance(adapted["options"], list):
                new_opts = []
                for opt in adapted["options"]:
                    if isinstance(opt, dict):
                        lbl = opt.get("label", "")
                        if isinstance(lbl, dict):
                            lbl = lbl.get(pref_lang) or lbl.get("English", "")
                        lbl = re.sub(r"\bresilience\b", "strength", lbl, flags=re.IGNORECASE)
                        lbl = re.sub(r"\bleadership\b", "helping friends", lbl, flags=re.IGNORECASE)
                        new_opts.append({"label": lbl, "value": opt.get("value", 0)})
                    else:
                        lbl = str(opt)
                        lbl = re.sub(r"\bresilience\b", "strength", lbl, flags=re.IGNORECASE)
                        lbl = re.sub(r"\bleadership\b", "helping friends", lbl, flags=re.IGNORECASE)
                        new_opts.append(lbl)
                adapted["options"] = new_opts
                
        elif complexity in ["SECONDARY", "SENIOR"]:
            if "career" not in prompt_val.lower() and "project" not in prompt_val.lower() and "business" not in prompt_val.lower():
                prompt_val = f"Future Planning / Scenario Analysis: {prompt_val}"
                
            if "options" in adapted and isinstance(adapted["options"], list):
                new_opts = []
                for opt in adapted["options"]:
                    if isinstance(opt, dict):
                        lbl = opt.get("label", "")
                        if isinstance(lbl, dict):
                            lbl = lbl.get(pref_lang) or lbl.get("English", "")
                        new_opts.append({"label": lbl, "value": opt.get("value", 0)})
                    else:
                        new_opts.append(opt)
                adapted["options"] = new_opts

    adapted["title"] = title_val
    adapted["prompt"] = prompt_val
    return adapted

def adapt_tasks_with_gemini(tasks, complexity, language, api_key):
    class_range = {
        "PRIMARY": "Classes 4-6",
        "MIDDLE": "Classes 7-8",
        "SECONDARY": "Classes 9-10",
        "SENIOR": "Classes 11-12"
    }[complexity]
    age_range = {
        "PRIMARY": "8-11 years",
        "MIDDLE": "12-14 years",
        "SECONDARY": "14-16 years",
        "SENIOR": "16-18 years"
    }[complexity]
    
    prompt = f"""
    You are a supportive child psychologist and expert psychometrician.
    Your task is to adapt the following list of assessment tasks to be age-appropriate for a student at the {complexity} level (Class range: {class_range}, Age: {age_range}).
    The preferred language is {language}.
    
    CRITICAL RULES FOR ADAPTATION:
    1. Maintain the EXACT same keys (like `key`, `type`, `domain`, `component`, `metric`) and data structures (options array length and order, sequence array length, etc.) for each task.
    2. Keep measuring the SAME underlying trait/component (e.g., leadership, mental rotation, etc.).
    3. Do NOT measure reading comprehension. Adapt the vocabulary and reading load to the specified level.
    4. Wording guidelines based on level:
       - PRIMARY (Class 4-6):
         * Readable within 5-8 seconds, max 20-25 words.
         * Emojis where helpful. Simple everyday vocabulary. No abstract psychological words (e.g., Motivation, Resilience, Empathy, Leadership, Reflection, Initiative, Strategic, Perspective, Analytical).
         * Game-like stories (adventures, missions, puzzles, detective challenges, treasure hunts, building challenges, team games).
         * Prefer concrete "What would you do?" situations.
       - MIDDLE (Class 7-8):
         * Medium reading complexity, 1-2 sentence scenarios.
         * Realistic school situations, sports teams, clubs, competitions, community activities.
         * Basic career concepts, slightly deeper reflection. Maintain gamification.
       - SECONDARY (Class 9-10):
         * Complex scenarios. Future planning, career exploration, sophisticated problem-solving. Deeper reflection.
         * Career choices, business ideas, technology, social challenges.
       - SENIOR (Class 11-12):
         * Full psychometric complexity, advanced reasoning.
         * Career/university situations, advanced self-reflection, ethical dilemmas, strategic planning, complex team leadership.
    5. Translate/localize both prompt, title, and options/labels to {language} (if it is Hindi, provide Hindi translations).
    
    Original Tasks to Adapt:
    {json.dumps(tasks, ensure_ascii=False)}
    
    Return ONLY a JSON array containing the adapted tasks. Each task in the array must contain all fields of the original task, with the `title`, `prompt`, `options`, `steps`, `shuffled`, `low`, `high` adapted according to the rules. Do not wrap in markdown other than the JSON block.
    """
    
    res = call_gemini_api(prompt, api_key)
    if res and isinstance(res, list) and len(res) == len(tasks):
        print(f"[SUCCESS] Successfully adapted {len(tasks)} tasks via Gemini API for {complexity} level.")
        return res
    print("[WARNING] Gemini adaptation failed or returned invalid JSON structure. Falling back to local rules.")
    return None

def generate_ai_tasks(child, discovery_answers):
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

    raw_tasks = []
    db_puzzles = load_puzzles_from_db()
    
    for domain in ["logical", "spatial", "creative", "language", "kinesthetic", "social", "naturalist", "intrapersonal"]:
        exp_val = child.get(f"exp_{domain}", 0)
        disc_count = discovery_counts.get(domain, 0)
        likelihood = exp_val + disc_count
        
        if likelihood >= 6:
            q_count = 6
        elif likelihood >= 3:
            q_count = 4
        else:
            q_count = 2
            
        domain_puzzles = [p for p in db_puzzles if p["domain"] == domain]
        selected = domain_puzzles[:q_count]
        
        for original_puzzle in selected:
            raw_tasks.append(original_puzzle)
            
    deep_discovery_tasks = [
        {
            "key": "deep_discovery_flow",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "self_awareness",
            "title": {"English": "Flow State Tracker", "Hindi": "ध्यान केंद्रित करने वाली गतिविधियाँ"},
            "prompt": {
                "English": "Tell us about an activity (like building, drawing, reading, or playing) that makes you completely lose track of time. What are you doing, and what makes it so exciting?",
                "Hindi": "हमें किसी ऐसी गतिविधि (जैसे कुछ बनाना, चित्र बनाना, पढ़ना, या खेलना) के बारे में बताएं जिसमें आप समय का ध्यान बिल्कुल भूल जाते हैं। आप क्या कर रहे होते हैं, और वह बात आपको इतनी रोमांचक क्यों लगती है?"
            }
        },
        {
            "key": "deep_discovery_pride",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "self_awareness",
            "title": {"English": "Your Proudest Moment", "Hindi": "आपका सबसे गौरवपूर्ण क्षण"},
            "prompt": {
                "English": "What is one project, creation, or achievement that you are most proud of? Describe what you did and why it felt so special to you.",
                "Hindi": "कोई एक प्रोजेक्ट, रचना, या उपलब्धि क्या है जिस पर आपको सबसे ज्यादा गर्व है? वर्णन करें कि आपने क्या किया और वह आपके लिए इतना विशेष क्यों था।"
            }
        },
        {
            "key": "deep_discovery_curiosity",
            "type": "open_ended",
            "domain": "intrapersonal",
            "component": "reflective_thinking",
            "title": {"English": "The One-Year Learning Quest", "Hindi": "एक साल का सीखने का सफर"},
            "prompt": {
                "English": "If you could spend one whole year learning about anything you want without any exams or grades, what topic or skill would you choose, and why?",
                "Hindi": "यदि आप बिना किसी परीक्षा या ग्रेड के अपनी पसंद की किसी भी चीज़ को सीखने में एक पूरा वर्ष बिता सकते हैं, तो आप किस विषय या कौशल को चुनेंगे, और क्यों?"
            }
        },
        {
            "key": "deep_discovery_vision",
            "type": "open_ended",
            "domain": "social",
            "component": "peer_influence",
            "title": {"English": "The Big Problem Solver", "Hindi": "बड़ी समस्या का समाधान"},
            "prompt": {
                "English": "If you were given resources to solve one big problem in your school, community, or the world, what problem would you choose, and how would you start solving it?",
                "Hindi": "यदि आपको अपने स्कूल, समुदाय या दुनिया में एक बड़ी समस्या को हल करने के लिए संसाधन दिए जाएं, तो आप कौन सी समस्या चुनेंगे, और आप इसे कैसे हल करना शुरू करेंगे?"
            }
        }
    ]
    
    for opt_task in deep_discovery_tasks:
        raw_tasks.append(opt_task)

    complexity = get_complexity_level(child.get("school_year"), child.get("age"))
    
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    adapted_tasks = None
    
    if api_key:
        try:
            adapted_tasks = adapt_tasks_with_gemini(raw_tasks, complexity, pref_lang, api_key)
        except Exception as e:
            print(f"[ERROR] Gemini adaptation failed: {e}. Falling back to local rules.")
            
    if not adapted_tasks:
        adapted_tasks = []
        for task in raw_tasks:
            try:
                adapted_tasks.append(adapt_task_locally(task, complexity, pref_lang))
            except Exception as e:
                print(f"[ERROR] Local adaptation failed for task {task.get('key')}: {e}")
                p = dict(task)
                p["title"] = task["title"].get(pref_lang, task["title"]["English"]) if isinstance(task.get("title"), dict) else task.get("title", "")
                p["prompt"] = task["prompt"].get(pref_lang, task["prompt"]["English"]) if isinstance(task.get("prompt"), dict) else task.get("prompt", "")
                adapted_tasks.append(p)
                
    return adapted_tasks

@app.route("/api/sessions/<int:sid>/discovery", methods=["POST"])
def submit_discovery(sid):
    user = current_user()
    
    data = request.json or {}
    answers = data.get("answers", {})
    child_id = data.get("child_id")
    print("==================================================")
    print(f"DEBUG: submit_discovery called for session ID: {sid} with data: {data}")
    
    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
    child = dict(child)
    
    if user:
        role = user.get("role")
        org_id = user.get("organization_id")
        center_id = user.get("center_id")
        
        if role != "master_admin":
            if child.get("organization_id") != org_id:
                return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
            if role != "admin" and child.get("center_id") is not None and child.get("center_id") != center_id:
                return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
                
            # Auto-assign center if currently unassigned and accessed by a facilitator
            if role != "admin" and child.get("center_id") is None and center_id is not None:
                print(f"DEBUG: Auto-assigning unassigned child {child_id} to center {center_id} on discovery submission")
                db.execute("UPDATE children SET center_id = ? WHERE id = ?", (center_id, child_id))
                db.commit()
                if supabase_client:
                    try:
                        supabase_client.table("children").update({"center_id": center_id}).eq("id", child_id).execute()
                    except Exception as e:
                        print(f"DEBUG: Exception auto-assigning child center on discovery: {e}")
                child["center_id"] = center_id
            
    generated_tasks = generate_ai_tasks(child, answers)
    
    if supabase_client:
        try:
            update_data = {
                "responses": json.dumps(answers),
                "generated_tasks": json.dumps(generated_tasks),
                "phase": "assess"
            }
            print(f"DEBUG: Attempting Supabase update for session ID: {sid} in discovery")
            # print(f"DEBUG: Supabase update payload: {json.dumps(update_data)}")
            res = supabase_client.table("sessions").update(update_data).eq("id", sid).execute()
            # print(f"DEBUG: Supabase update response data: {res.data}")
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase update in discovery: {str(e)[:200]}")
            
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
@app.route("/api/sessions/<int:sid>/submit/", methods=["POST"])
def submit_session(sid):
    """
    Receives all responses, runs the scoring engine, saves results.
    """
    return analyze_and_save_session(sid, request.json)

@app.route("/api/sessions/<int:sid>/analyze", methods=["POST"])
@app.route("/api/sessions/<int:sid>/analyze/", methods=["POST"])
def analyze_session(sid):
    """
    Receives structured questionnaire and puzzle responses, analyses metrics,
    saves results, and returns the computed profile.
    """
    return analyze_and_save_session(sid, request.json)

def analyze_and_save_session(sid, data):
    user = current_user()
    
    print("==================================================")
    print(f"DEBUG: analyze_and_save_session called for session ID: {sid}")
    try:
        print(f"DEBUG: Incoming assessment data responses count: {len(data.get('responses', {})) if data else 0}")
        # print(f"DEBUG: Incoming assessment data: {json.dumps(data)}")
    except Exception as e:
        print(f"DEBUG: Error printing incoming data: {e}")
        
    data = data or {}
    responses = data.get("responses", {})
    child_id = data.get("child_id")

    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
    child = dict(child)

    if user:
        role = user.get("role")
        org_id = user.get("organization_id")
        center_id = user.get("center_id")
        
        if role != "master_admin":
            if child.get("organization_id") != org_id:
                return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
            if role != "admin" and child.get("center_id") is not None and child.get("center_id") != center_id:
                return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
                
            # Auto-assign center if currently unassigned and accessed by a facilitator
            if role != "admin" and child.get("center_id") is None and center_id is not None:
                print(f"DEBUG: Auto-assigning unassigned child {child_id} to center {center_id} on analysis/submission")
                db.execute("UPDATE children SET center_id = ? WHERE id = ?", (center_id, child_id))
                db.commit()
                if supabase_client:
                    try:
                        supabase_client.table("children").update({"center_id": center_id}).eq("id", child_id).execute()
                    except Exception as e:
                        print(f"DEBUG: Exception auto-assigning child center on analysis: {e}")
                child["center_id"] = center_id

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

    # Calculate past completed sessions count
    past_sessions_count = 0
    try:
        past_sessions = db.execute(
            "SELECT COUNT(*) as count FROM sessions WHERE child_id = ? AND status = 'complete' AND id != ?",
            (child["id"], sid)
        ).fetchone()
        if past_sessions:
            past_sessions_count = past_sessions["count"]
    except Exception as e:
        print(f"DEBUG: Exception calculating past sessions count: {e}")

    # Run scoring engine with full context
    scores = score_responses(responses, child, discovery_answers, latest_note, past_sessions_count=past_sessions_count)

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
    
    # Extract open-ended answers from responses payload
    open_ended_answers = {}
    for k, v in responses.items():
        if isinstance(v, dict) and v.get("task_type") == "open_ended":
            open_ended_answers[k] = v.get("value", "")

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
        
        Qualitative Deep Discovery Responses (simple text inputs from child):
        - Flow State (what makes them lose track of time): "{open_ended_answers.get("deep_discovery_flow", "None provided")}"
        - Proudest Achievement: "{open_ended_answers.get("deep_discovery_pride", "None provided")}"
        - One-Year Quest (what they would choose to learn): "{open_ended_answers.get("deep_discovery_curiosity", "None provided")}"
        - Big Problem Solver (their future vision/problem solving): "{open_ended_answers.get("deep_discovery_vision", "None provided")}"
        
        Please analyze this data and generate a JSON object with two fields (do not write any markdown outside the JSON block):
        - "talent_narrative": A warm, encouraging, human, and educator-friendly narrative (2-3 sentences) explaining the child's natural abilities and learning style, synthesizing the quantitative scores with their qualitative deep discovery answers.
          Always communicate probability and potential rather than certainty (e.g. "suggests strong indicators in X activities" rather than "X is your greatest strength").
          Avoid all corporate buzzwords or definitive labels. Focus on spontaneous behaviors.
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

        flow_text = open_ended_answers.get("deep_discovery_flow", "")
        interest_ref = f" especially related to their interest in '{flow_text[:50]}...'" if flow_text else ""

        talent_narrative = (
            f"{child.get('name', 'This child')} showed the strongest indicators in {primary_label} activities{interest_ref}, "
            f"particularly in {task_str} tasks. {sec_str} also emerged as a promising area for potential development. "
            f"Because prior exposure in this domain appears {exposure_label}, additional workshops and continued "
            f"participation may provide a clearer picture of their long-term strengths.{potential_str}"
        )
        pattern_analysis = f"Deductive problem-solving speed was balanced. Memory and attention were stable throughout scored cognitive challenges. Divergence levels show strong flexible reasoning."

    # 1. Resolve Personas
    top_3_list = [scores["primary_domain"]] + scores["secondary_domains"]
    personas = resolve_personas(top_3_list)

    # 2. Extract NLP signals
    nlp_signals = extract_nlp_signals(open_ended_answers, api_key)

    # 3. Generate Roadmap
    sec_dom = scores["secondary_domains"][0] if scores["secondary_domains"] else scores["primary_domain"]
    roadmap = generate_dynamic_roadmap(scores["primary_domain"], sec_dom, child.get("age", 12), final_scores, child, api_key)

    # 4. Generate Workshops
    workshops = generate_workshop_recommendations(scores["primary_domain"], sec_dom)

    # 5. Career Pathways
    career_pathways = get_career_pathways(scores["primary_domain"], sec_dom, child.get("school_year", ""))

    personality_val = {
        "metrics": scores["metrics"],
        "facilitator_adjustment": fac_adjustment,
        "evidence": scores["evidence"],
        "confidence_level": scores["confidence_level"],
        "confidence_score": scores["confidence_score"],
        "confidence_desc": scores["confidence_desc"],
        "evidence_sources": scores["evidence_sources"],
        "untapped_potential": scores["untapped_potential"],
        "primary_domain": scores["primary_domain"],
        "secondary_domains": scores["secondary_domains"],
        "emerging_domains": scores["emerging_domains"],
        "talent_narrative": talent_narrative,
        "pattern_analysis": pattern_analysis,
        "separation_index": scores["separation_index"],
        "multiple_talents_detected": scores["multiple_talents_detected"],
        "action_plan": scores["action_plan"],
        "personas": personas,
        "nlp_signals": nlp_signals,
        "gti_score": scores["gti_score"],
        "gti_label": scores["gti_label"],
        "teg_data": scores["teg_data"],
        "roadmap": roadmap,
        "workshops": workshops,
        "career_pathways": career_pathways,
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
            # print(f"DEBUG: Supabase update payload: {json.dumps(update_data)}")
            res = supabase_client.table("sessions").update(update_data).eq("id", sid).execute()
            # print(f"DEBUG: Supabase update response data: {res.data}")
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase update: {str(e)[:200]}")

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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    # Check child scope first
    child = db.execute("SELECT * FROM children WHERE id=?", (cid,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    child_dict = dict(child)
    if role != "master_admin":
        if child_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    data = request.json or {}
    child_id = data.get("child_id")
    
    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    child_dict = dict(child)
    if role != "master_admin":
        if child_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
    facilitator_name = data.get("facilitator") or (user["name"] if user else "GOAT Mentor")

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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    # Check session/child scope
    session_row = db.execute("SELECT s.*, c.organization_id, c.center_id FROM sessions s JOIN children c ON s.child_id = c.id WHERE s.id=?", (sid,)).fetchone()
    if not session_row:
        return jsonify({"error": "Session not found"}), 404
        
    session_dict = dict(session_row)
    if role != "master_admin":
        if session_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Session belongs to another organization"}), 403
        if role != "admin" and session_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Session belongs to another center"}), 403
            
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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    data = request.json or {}
    child_id = data.get("child_id")
    mentor_id = data.get("mentor_id")
    domain = data.get("domain", "")
    
    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    child_dict = dict(child)
    if role != "master_admin":
        if child_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403

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
        if not isinstance(db, PostgresConnectionWrapper):
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
        else:
            print("DEBUG: Postgres connection active. Skipping redundant local insert for match/milestones as Supabase client has already inserted.")
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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    # Check child scope first
    child = db.execute("SELECT * FROM children WHERE id=?", (cid,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    child_dict = dict(child)
    if role != "master_admin":
        if child_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    # Check if match exists and its child belongs to scoped org/center
    match = db.execute("""
        SELECT mm.*, c.organization_id, c.center_id
        FROM mentor_matches mm
        JOIN children c ON mm.child_id = c.id
        WHERE mm.id = ?
    """, (mid,)).fetchone()
    if not match:
        return jsonify({"error": "Match not found"}), 404
        
    match_dict = dict(match)
    if role != "master_admin":
        if match_dict.get("organization_id") != org_id:
            return jsonify({"error": "Forbidden: Match belongs to another organization"}), 403
        if role != "admin" and match_dict.get("center_id") != center_id:
            return jsonify({"error": "Forbidden: Match belongs to another center"}), 403

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
    user, error = require_user()
    if error:
        return error
        
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    if role == "master_admin":
        total_children  = db.execute("SELECT COUNT(*) FROM children").fetchone()[0]
        total_sessions  = db.execute("SELECT COUNT(*) FROM sessions WHERE status='complete'").fetchone()[0]
        total_matches   = db.execute("SELECT COUNT(*) FROM mentor_matches").fetchone()[0]
        domain_dist     = db.execute("""
            SELECT top_domain, COUNT(*) as cnt
            FROM sessions WHERE status='complete' AND top_domain IS NOT NULL
            GROUP BY top_domain ORDER BY cnt DESC
        """).fetchall()
    elif role == "admin": # Org Admin
        total_children  = db.execute("SELECT COUNT(*) FROM children WHERE organization_id=?", (org_id,)).fetchone()[0]
        total_sessions  = db.execute("""
            SELECT COUNT(*) FROM sessions s 
            JOIN children c ON s.child_id = c.id 
            WHERE s.status='complete' AND c.organization_id=?
        """, (org_id,)).fetchone()[0]
        total_matches   = db.execute("""
            SELECT COUNT(*) FROM mentor_matches mm 
            JOIN children c ON mm.child_id = c.id 
            WHERE c.organization_id=?
        """, (org_id,)).fetchone()[0]
        domain_dist     = db.execute("""
            SELECT s.top_domain, COUNT(*) as cnt
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND s.top_domain IS NOT NULL AND c.organization_id=?
            GROUP BY s.top_domain ORDER BY cnt DESC
        """, (org_id,)).fetchall()
    else: # Facilitator, etc.
        total_children  = db.execute("SELECT COUNT(*) FROM children WHERE organization_id=? AND center_id=?", (org_id, center_id)).fetchone()[0]
        total_sessions  = db.execute("""
            SELECT COUNT(*) FROM sessions s 
            JOIN children c ON s.child_id = c.id 
            WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
        """, (org_id, center_id)).fetchone()[0]
        total_matches   = db.execute("""
            SELECT COUNT(*) FROM mentor_matches mm 
            JOIN children c ON mm.child_id = c.id 
            WHERE c.organization_id=? AND c.center_id=?
        """, (org_id, center_id)).fetchone()[0]
        domain_dist     = db.execute("""
            SELECT s.top_domain, COUNT(*) as cnt
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND s.top_domain IS NOT NULL AND c.organization_id=? AND c.center_id=?
            GROUP BY s.top_domain ORDER BY cnt DESC
        """, (org_id, center_id)).fetchall()

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
        "week_4": "Navigation Walk: Draw a detailed map of the route from your home to the center, indicating major landmarks."
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

def get_text_completion_score(val):
    if not val:
        return 0.0
    text = ""
    if isinstance(val, dict):
        text = val.get("value", "") or val.get("text", "") or ""
    else:
        text = str(val)
    words = len(text.strip().split())
    if words >= 15:
        return 100.0
    elif words >= 5:
        return 60.0
    elif words > 0:
        return 30.0
    return 0.0

def local_nlp_extract(open_ended):
    signals = {}
    
    # 1. Curiosity
    q_text = (open_ended.get("deep_discovery_curiosity", "") or "").lower()
    if any(k in q_text for k in ["learn", "why", "how", "know", "science", "read", "explore", "discover", "cautious"]):
        signals["curiosity"] = {"status": True, "evidence": f"Expressed clear learning interest: '{open_ended.get('deep_discovery_curiosity')[:60]}...'"}
    else:
        signals["curiosity"] = {"status": False, "evidence": "No clear curiosity indicators detected in written response."}
        
    # 2. Self-awareness & Reflection
    pride_text = (open_ended.get("deep_discovery_pride", "") or "").lower()
    if any(k in pride_text for k in ["proud", "feel", "happy", "made", "build", "create", "achieve", "win"]):
        signals["self_awareness"] = {"status": True, "evidence": f"Reflected on personal milestone: '{open_ended.get('deep_discovery_pride')[:60]}...'"}
        signals["reflection"] = {"status": True, "evidence": "Reflective thinking shown in proudest achievement description."}
    else:
        signals["self_awareness"] = {"status": False, "evidence": "Self-awareness indicators are exploratory in self-reflection response."}
        signals["reflection"] = {"status": False, "evidence": "Reflection indicators are exploratory."}

    # 3. Imagination & Creativity
    flow_text = (open_ended.get("deep_discovery_flow", "") or "").lower()
    if any(k in flow_text for k in ["draw", "art", "paint", "build", "craft", "make", "blocks", "play", "game", "write"]):
        signals["imagination"] = {"status": True, "evidence": f"Described immersive creative activity: '{open_ended.get('deep_discovery_flow')[:60]}...'"}
    else:
        signals["imagination"] = {"status": False, "evidence": "Imagination indicators are exploratory."}

    # 4. Problem-solving & Leadership
    vision_text = (open_ended.get("deep_discovery_vision", "") or "").lower()
    if any(k in vision_text for k in ["solve", "help", "school", "people", "clean", "tree", "plant", "water", "food"]):
        signals["problem_solving"] = {"status": True, "evidence": f"Offered community problem-solving vision: '{open_ended.get('deep_discovery_vision')[:60]}...'"}
        signals["leadership"] = {"status": True, "evidence": "Considers collective benefit and peer organization in future vision."}
    else:
        signals["problem_solving"] = {"status": False, "evidence": "Problem-solving indicators are exploratory."}
        signals["leadership"] = {"status": False, "evidence": "Leadership indicators are exploratory."}

    # 5. EQ
    if any("feel" in t or "help" in t or "friend" in t for t in [flow_text, pride_text, q_text, vision_text]):
        signals["eq"] = {"status": True, "evidence": "Demonstrated empathy and social awareness in descriptions."}
    else:
        signals["eq"] = {"status": False, "evidence": "EQ indicators are exploratory."}

    # 6. Communication Style
    total_len = sum(len(t.split()) for t in open_ended.values() if isinstance(t, str))
    if total_len > 40:
        signals["communication_style"] = {"status": True, "evidence": f"Descriptive and detailed communication style ({total_len} words total)."}
    else:
        signals["communication_style"] = {"status": False, "evidence": "Concise and brief communication style."}

    return signals

def get_parent_intelligence(primary):
    playbook = {
        "creative": {
            "motivators": "Open-ended projects, visual design choices, creative writing, and self-expression.",
            "discouragers": "Highly repetitive rote tasks, lack of autonomy, and rigid step-by-step rules.",
            "environments": "Design labs, art studios, project-based learning centers, and sensory-rich spaces."
        },
        "spatial": {
            "motivators": "Constructing physical/3D models, mechanical diagrams, scale drawings, and hands-on tools.",
            "discouragers": "Sitting for long hours of purely passive listening or lecture-based study.",
            "environments": "Maker spaces, robotics studios, carpentry/craft shops, and interactive museums."
        },
        "logical": {
            "motivators": "Structured mathematical pattern puzzles, strategy games like chess, and coding challenges.",
            "discouragers": "Vague goals, emotional arguments with no logical resolution, and arbitrary rule-making.",
            "environments": "STEM labs, chess/board-game clubs, computer labs, and debate chambers."
        },
        "social": {
            "motivators": "Group discussions, collaborative team activities, leading peers, and helping friends.",
            "discouragers": "Prolonged isolated work, lack of human interaction, and competitive individual ranking systems.",
            "environments": "Student council rooms, community volunteer spaces, group workspace layouts, and team sports."
        },
        "language": {
            "motivators": "Storytelling, writing scripts, debates, giving speeches, and playing word games.",
            "discouragers": "Rote visual transcription without verbal reasoning or discussion.",
            "environments": "Drama stages, debate chambers, reading clubs, and writing seminars."
        },
        "naturalist": {
            "motivators": "Eco-trails, planting seeds, observing micro-ecosystems, and classification of plants/animals.",
            "discouragers": "Completely desk-bound instruction, sterile environments with no window light or plants.",
            "environments": "Botanical gardens, conservation areas, school greenhouse yards, and nature trails."
        },
        "kinesthetic": {
            "motivators": "Agility games, dancing, physical sports, and direct hand-on testing of materials.",
            "discouragers": "Sedentary classroom lectures, lack of physical breaks, and purely abstract conceptual study.",
            "environments": "Gymnasiums, dance studios, sports complexes, and experiential building zones."
        },
        "intrapersonal": {
            "motivators": "Independent goals, journal writing, quiet reflection, and self-selected learning topics.",
            "discouragers": "Highly chaotic or competitive team settings with zero personal quiet time.",
            "environments": "Quiet libraries, individual study booths, cozy corners, and self-guided project rooms."
        }
    }
    return playbook.get(primary, playbook["logical"])

def get_career_pathways(primary, secondary, school_year):
    pathways = {
        "creative": {
            "careers": ["Interaction/UI Designer", "Creative Director", "Architect", "Animator"],
            "projects": ["Build a personal digital art folio", "Write and illustrate a comic book"],
            "competitions": ["National Junior Art Contest", "School Design-a-Thon"],
            "tracks": ["Visual Arts & Animation", "UX/UI Design & Creative Writing"]
        },
        "spatial": {
            "careers": ["Robotics Engineer", "Civil Engineer", "Industrial Product Designer", "Urban Planner"],
            "projects": ["Design a cardboard bridge model that supports 5kg", "Program a robotic arm model"],
            "competitions": ["Junior Robotics Olympiad", "Bridge Building Competition"],
            "tracks": ["Engineering & CAD Modeling", "Product Design & Robotics"]
        },
        "logical": {
            "careers": ["Data Scientist", "Software Engineer", "Systems Analyst", "Financial Quant"],
            "projects": ["Analyze school attendance patterns using spreadsheets", "Build a python text-adventure game"],
            "competitions": ["Mathematics Olympiad", "CodeForces Junior Hackathon"],
            "tracks": ["Computer Science & Algorithms", "Advanced Statistics & Mathematics"]
        },
        "social": {
            "careers": ["Project Manager", "Organization Director", "Human Resources Head", "Public Relations Expert"],
            "projects": ["Coordinate a school-wide recycling drive", "Lead a student volunteer group"],
            "competitions": ["Social Entrepreneurship Pitch Challenge", "Youth Leadership Summit"],
            "tracks": ["Management & Communications", "Public Policy & Social Innovation"]
        },
        "language": {
            "careers": ["Journalist", "Public Speaker/Advocate", "Content Editor", "Legal Advisor"],
            "projects": ["Publish a school newsletter", "Write and record a 3-episode audio podcast"],
            "competitions": ["National School Debate Championship", "Model United Nations (MUN)"],
            "tracks": ["Journalism & Media", "Pre-Law & Rhetoric Studies"]
        },
        "naturalist": {
            "careers": ["Environmental Scientist", "Agricultural Specialist", "Conservation Biologist", "Veterinarian"],
            "projects": ["Build a water filtration model", "Establish a native butterfly patch at school"],
            "competitions": ["Eco-Innovation Fair", "Science & Botany Olympiad"],
            "tracks": ["Environmental Engineering", "Botany & Animal Health Science"]
        },
        "kinesthetic": {
            "careers": ["Physical Therapist", "Athletic Coach", "Choreographer", "Product Safety Tester"],
            "projects": ["Create a weekly core agility exercise manual", "Choreograph a team dance routine"],
            "competitions": ["Athletic Decathlon", "State Choreography Competition"],
            "tracks": ["Kinesiology & Athletic Coaching", "Performing Arts & Ergonomic Design"]
        },
        "intrapersonal": {
            "careers": ["Research Scientist", "Psychologist/Counselor", "Strategic Planner", "Writer/Scholar"],
            "projects": ["Log 30 days of emotional response mapping", "Write a personal philosophy journal"],
            "competitions": ["Social Sciences Research Paper Exhibit", "Creative Writing Portfolio Review"],
            "tracks": ["Psychology & Behavioral Studies", "Philosophy & Scientific Research Methodologies"]
        }
    }
    p_path = pathways.get(primary, pathways["logical"])
    s_path = pathways.get(secondary, pathways["creative"])
    return {
        "careers": list(set(p_path["careers"][:2] + s_path["careers"][:2])),
        "projects": [p_path["projects"][0], s_path["projects"][0]],
        "competitions": [p_path["competitions"][0], s_path["competitions"][0]],
        "tracks": [p_path["tracks"][0], s_path["tracks"][0]]
    }

def generate_workshop_recommendations(primary, secondary):
    workshops_map = {
        "creative": {"title": "Art & Design", "desc": "Explore visual composition, painting, and digital sketching."},
        "logical": {"title": "STEM & Coding", "desc": "Learn block-based coding, logical circuits, and math puzzles."},
        "spatial": {"title": "Tinkering & Making", "desc": "Hands-on model building, electronics assembly, and woodworking."},
        "social": {"title": "Peer Leadership", "desc": "Public speaking, coordination games, and community projects."},
        "language": {"title": "Debate & Storytelling", "desc": "Scriptwriting, poetry slams, and team debates."},
        "naturalist": {"title": "Young Naturalist Trails", "desc": "Nature mapping, ecology walks, and soil chemistry investigations."},
        "kinesthetic": {"title": "Sports & Movement", "desc": "Agility routines, gymnastics, coordination drills, and dance."},
        "intrapersonal": {"title": "Goal Setting & Reflective Writing", "desc": "Mindfulness practices, logging milestones, and emotional journaling."}
    }
    p_ws = workshops_map.get(primary, workshops_map["logical"])
    s_ws = workshops_map.get(secondary, workshops_map["creative"])
    rationale = (
        f"Although {primary.capitalize()} is the dominant strength, integrating {secondary.capitalize()} "
        f"activities will strengthen complementary capabilities, building a well-rounded skill pathway."
    )
    return [
        {"title": p_ws["title"], "desc": p_ws["desc"], "reason": f"Nurtures the primary cognitive strength in {primary}."},
        {"title": s_ws["title"], "desc": s_ws["desc"], "reason": rationale}
    ]

def generate_dynamic_roadmap(primary, secondary, age, scores, child, api_key=None):
    try:
        age_val = int(age)
    except Exception:
        age_val = 12
        
    if age_val <= 9:
        age_bracket = "PRIMARY (Ages 6-9)"
    elif age_val <= 12:
        age_bracket = "MIDDLE (Ages 10-12)"
    elif age_val <= 14:
        age_bracket = "SECONDARY (Ages 13-14)"
    else:
        age_bracket = "SENIOR (Ages 15+)"

    if api_key:
        prompt = f"""
        You are an expert child development specialist and curriculum designer.
        Create a personalized 4-week talent development roadmap for a child named {child.get("name", "the child")} (Age {age_val}, Bracket: {age_bracket}).
        Natural strengths:
        - Primary strength: {primary.capitalize()} (score: {scores.get(primary, 85)})
        - Secondary strength: {secondary.capitalize()} (score: {scores.get(secondary, 75)})
        
        Generate a 4-week schedule that blends both domains:
        - Week 1: Introductory {primary.capitalize()} Project
        - Week 2: Complementary {secondary.capitalize()} Skill
        - Week 3: Advanced {primary.capitalize()} Integration
        - Week 4: Cross-Domain Milestone (combining {primary.capitalize()} and {secondary.capitalize()})

        For each week, define:
        1. "title": A descriptive activity title
        2. "expected_outcome": What the child will achieve by the end of the week (adjusted for {age_bracket})
        3. "parent_action": A specific action or support role for the parent
        4. "mentor_action": A guidance, reviewing, or coaching action for the mentor

        Please respond with a raw JSON block only (no markdown, no formatting, no wrapper) containing a dict with keys: week_1, week_2, week_3, week_4.
        Example structure:
        {{
           "week_1": {{ "title": "...", "expected_outcome": "...", "parent_action": "...", "mentor_action": "..." }},
           ...
        }}
        """
        try:
            res = call_gemini_api(prompt, api_key)
            if res and isinstance(res, dict) and "week_1" in res:
                return res
        except Exception as e:
            print(f"DEBUG: Gemini roadmap generation exception: {e}")

    prim_acts = {
        "creative": [
            {"title": "Visual Storyboard Project", "expected_outcome": "Complete a 4-panel storyboard illustrating a personal story", "parent_action": "Provide sketching supplies and ask them to explain the characters", "mentor_action": "Review the narrative flow and give constructive encouragement"},
            {"title": "Open-Ended Redesign Challenge", "expected_outcome": "Redesign a common household object with 3 new functions", "parent_action": "Help find recyclable items like cardboard/plastic for building", "mentor_action": "Discuss utility vs aesthetics in the design concept"}
        ],
        "spatial": [
            {"title": "3D Scale Model Building", "expected_outcome": "Construct a scale model of a room or dream house", "parent_action": "Provide cardboard, ruler, glue, and a tape measure", "mentor_action": "Review scale ratios and structural stability"},
            {"title": "Mechanical Assembly Investigation", "expected_outcome": "Take apart an old toy/device to diagram its moving parts", "parent_action": "Provide simple screwdrivers and supervise safety", "mentor_action": "Explain gears, pivots, or linkage systems"}
        ],
        "logical": [
            {"title": "Sequence Cryptography Quest", "expected_outcome": "Create and solve a 5-step cipher puzzle for family members", "parent_action": "Try solving the child's cipher and discuss patterns", "mentor_action": "Introduce basic number systems or binary coding concepts"},
            {"title": "Logic Matrix Design", "expected_outcome": "Construct a grid puzzle representing a deductive mystery", "parent_action": "Discuss how clue conditions isolate unique variables", "mentor_action": "Evaluate the mathematical logical soundness of the puzzle"}
        ],
        "social": [
            {"title": "Community Project Coordinator", "expected_outcome": "Plan a small community or household cleanup activity", "parent_action": "Support coordinating with neighbors and join the cleanup", "mentor_action": "Provide tips on delegation and motivating team members"},
            {"title": "Classroom Activity Facilitation", "expected_outcome": "Organize and lead a group game for 4+ friends", "parent_action": "Provide snacks and space for friends to gather", "mentor_action": "Reflect on how conflicts were handled and how to listen"}
        ],
        "language": [
            {"title": "Public Speaking Storytelling", "expected_outcome": "Deliver a 3-minute oral presentation about a favorite topic", "parent_action": "Listen to practice runs and film a short clip", "mentor_action": "Coach on voice modulation, eye contact, and pacing"},
            {"title": "Dialogue Script Writing", "expected_outcome": "Write a 2-page theatrical dialogue script between two characters", "parent_action": "Read one of the characters' parts aloud with them", "mentor_action": "Provide feedback on character voice and narrative hook"}
        ],
        "naturalist": [
            {"title": "Local Biodiversity Survey", "expected_outcome": "Map and classify 10 distinct plant or insect species in area", "parent_action": "Accompany on a park walk and help photograph species", "mentor_action": "Explain botanical/zoological classification families"},
            {"title": "Micro-Ecosystem Observation", "expected_outcome": "Log soil humidity and organism activity in a 1-meter zone", "parent_action": "Help set up a small garden pot or compost bin", "mentor_action": "Introduce ecological cycles and decomposer concepts"}
        ],
        "kinesthetic": [
            {"title": "Obstacle Course Coordination", "expected_outcome": "Design and time a physical movement layout with 5 stages", "parent_action": "Supervise safety and track execution times with a stopwatch", "mentor_action": "Discuss biomechanical control and motor planning"},
            {"title": "Rhythmic Coordination Routine", "expected_outcome": "Perform a coordinated rhythm sequence using feet and hands", "parent_action": "Clap along and practice the rhythm together", "mentor_action": "Review syncopation and movement memory pacing"}
        ],
        "intrapersonal": [
            {"title": "Mindfulness Goal Mapping", "expected_outcome": "Log daily practice times and write emotional reflections", "parent_action": "Allocate 15 minutes of quiet time at home each evening", "mentor_action": "Review goal-setting logs and coach on stress resilience"},
            {"title": "Reflective Essay Journal", "expected_outcome": "Write a 1-page essay outlining personal growth and hurdles", "parent_action": "Discuss the essay with them, sharing personal hurdle stories", "mentor_action": "Provide validation and help construct action milestones"}
        ]
    }
    
    p_acts_raw = prim_acts.get(primary, prim_acts["logical"])
    s_acts_raw = prim_acts.get(secondary, prim_acts["creative"])
    
    def adapt_activity(act, bracket):
        adapted = act.copy()
        if bracket == "PRIMARY (Ages 6-9)":
            adapted["expected_outcome"] += " (adapted for younger children: focus on basic exploration and simple steps)"
            adapted["parent_action"] = "Support closely: " + adapted["parent_action"]
        elif bracket == "SECONDARY (Ages 13-14)":
            adapted["expected_outcome"] += " (adapted for middle schoolers: add research notes or a digital presentation component)"
            adapted["mentor_action"] = "Guide critical thinking: " + adapted["mentor_action"]
        elif bracket == "SENIOR (Ages 15+)":
            adapted["expected_outcome"] += " (adapted for older youth: focus on real-world utility, documentation, and advanced tools)"
            adapted["mentor_action"] = "Challenge with industry-standard practices: " + adapted["mentor_action"]
        return adapted

    p_acts = [adapt_activity(a, age_bracket) for a in p_acts_raw]
    s_acts = [adapt_activity(a, age_bracket) for a in s_acts_raw]

    return {
        "week_1": {
            "title": f"Introductory {primary.capitalize()} Project: {p_acts[0]['title']}",
            "expected_outcome": p_acts[0]["expected_outcome"],
            "parent_action": p_acts[0]["parent_action"],
            "mentor_action": p_acts[0]["mentor_action"]
        },
        "week_2": {
            "title": f"Complementary {secondary.capitalize()} Skill: {s_acts[0]['title']}",
            "expected_outcome": s_acts[0]["expected_outcome"],
            "parent_action": s_acts[0]["parent_action"],
            "mentor_action": s_acts[0]["mentor_action"]
        },
        "week_3": {
            "title": f"Advanced {primary.capitalize()} Integration: {p_acts[1]['title']}",
            "expected_outcome": p_acts[1]["expected_outcome"],
            "parent_action": p_acts[1]["parent_action"],
            "mentor_action": p_acts[1]["mentor_action"]
        },
        "week_4": {
            "title": f"Cross-Domain Milestone: {s_acts[1]['title']}",
            "expected_outcome": f"Synthesize {primary.capitalize()} with {secondary.capitalize()}: {s_acts[1]['expected_outcome']}",
            "parent_action": s_acts[1]["parent_action"],
            "mentor_action": s_acts[1]["mentor_action"]
        }
    }

def resolve_personas(top_3):
    persona_mapping = {
        "creative": {"title": "The Creator", "emoji": "🎨", "desc": "Enjoys generating original ideas, imagining possibilities, and expressing thoughts through visual and artistic mediums."},
        "spatial": {"title": "The Builder", "emoji": "🔧", "desc": "Thinks in three dimensions, loves constructing physical or mental models, and naturally understands design structures."},
        "logical": {"title": "The Thinker", "emoji": "🧠", "desc": "Highly analytical, naturally notices logical patterns, loves solving puzzles, and thrives on structured reasoning."},
        "social": {"title": "The Leader", "emoji": "🤝", "desc": "Possesses natural social intelligence, easily connects with others, coordinates collaborative activities, and guides groups."},
        "language": {"title": "The Communicator", "emoji": "💬", "desc": "Natural affinity for words, excels in verbal storytelling, expresses ideas with high clarity, and loves debate."},
        "naturalist": {"title": "The Observer", "emoji": "🌱", "desc": "Unusual detail-awareness in nature, notices micro-patterns in ecosystems, and loves classifying details."},
        "kinesthetic": {"title": "The Explorer", "emoji": "🏃", "desc": "Learns best through physical doing, movement, and hands-on trial-and-error, showing great motor control."},
        "intrapersonal": {"title": "The Researcher", "emoji": "🧘", "desc": "Exhibits deep self-awareness, prefers reflecting in quiet spaces, understands personal motivations, and sets goals."}
    }
    p = persona_mapping.get(top_3[0], persona_mapping["logical"])
    s = persona_mapping.get(top_3[1], persona_mapping["creative"])
    e = persona_mapping.get(top_3[2], persona_mapping["kinesthetic"])
    prim_pi = get_parent_intelligence(top_3[0])
    sec_pi = get_parent_intelligence(top_3[1])
    emg_pi = get_parent_intelligence(top_3[2])
    recs = {
        "creative": {"strengths": ["Vivid Imagination", "Divergent Thinking"], "growth": ["Structured Completion", "Attention to Rules"]},
        "spatial": {"strengths": ["3D Visualization", "Structural Logic"], "growth": ["Verbalizing Concepts", "Patience with Theory"]},
        "logical": {"strengths": ["Pattern Recognition", "Reasoning & Logic"], "growth": ["Handling Vague Goals", "Accepting Ambiguity"]},
        "social": {"strengths": ["Empathy & Influence", "Group Organization"], "growth": ["Delegating Tasks", "Sustaining Quiet Focus"]},
        "language": {"strengths": ["Verbal Fluency", "Narrative Structure"], "growth": ["Listening Carefully", "Silent Individual Practice"]},
        "naturalist": {"strengths": ["Sensory Observation", "Taxonomic Classification"], "growth": ["Abstract Symbolic Tasks", "Sedentary Study"]},
        "kinesthetic": {"strengths": ["Fine-Motor Precision", "Coordination & Agility"], "growth": ["Passive Auditory Learning", "Prolonged Sitting"]},
        "intrapersonal": {"strengths": ["Emotional Reflexivity", "Independent Planning"], "growth": ["Highly Competitive Groups", "Spontaneous Speaking"]}
    }
    p_rec = recs.get(top_3[0], recs["logical"])
    s_rec = recs.get(top_3[1], recs["creative"])
    e_rec = recs.get(top_3[2], recs["kinesthetic"])
    return {
        "primary": {
            "key": top_3[0],
            "title": p["title"],
            "emoji": p["emoji"],
            "desc": p["desc"],
            "strengths": p_rec["strengths"],
            "growth": p_rec["growth"],
            "environments": [prim_pi["environments"]]
        },
        "secondary": {
            "key": top_3[1],
            "title": s["title"],
            "emoji": s["emoji"],
            "desc": s["desc"],
            "strengths": s_rec["strengths"],
            "growth": s_rec["growth"],
            "environments": [sec_pi["environments"]]
        },
        "emerging": {
            "key": top_3[2],
            "title": e["title"],
            "emoji": e["emoji"],
            "desc": e["desc"],
            "strengths": e_rec["strengths"],
            "growth": e_rec["growth"],
            "environments": [emg_pi["environments"]]
        }
    }

def calculate_gti(sorted_domains):
    if not sorted_domains:
        return 0, "Explorer"
    top_1 = sorted_domains[0][1] if len(sorted_domains) > 0 else 0
    top_2 = sorted_domains[1][1] if len(sorted_domains) > 1 else 0
    top_3 = sorted_domains[2][1] if len(sorted_domains) > 2 else 0
    
    gti_score = int(round(0.5 * top_1 + 0.3 * top_2 + 0.2 * top_3))
    
    if gti_score < 50:
        gti_label = "Explorer"
    elif gti_score <= 64:
        gti_label = "Emerging"
    elif gti_score <= 74:
        gti_label = "Developing"
    elif gti_score <= 84:
        gti_label = "Advanced"
    else:
        gti_label = "Exceptional"
        
    return gti_score, gti_label

def calculate_teg(final_scores, child):
    teg_data = {}
    for domain, talent_score in final_scores.items():
        exp_val = child.get(f"exp_{domain}", 0)
        exposure_score = int(round((exp_val / 3.0) * 100))
        
        opportunity_score = min(100, int(round((talent_score + (100 - exposure_score)) * 0.56)))
        
        if talent_score >= 75 and exposure_score <= 33:
            teg_status = "High Potential, Low Exposure"
        elif talent_score >= 75 and exposure_score > 66:
            teg_status = "Nurtured Strength"
        elif talent_score >= 75 and 33 < exposure_score <= 66:
            teg_status = "Active Development"
        elif 50 <= talent_score < 75 and exposure_score <= 50:
            teg_status = "Developing Potential"
        else:
            teg_status = "Exploratory"
            
        teg_data[domain] = {
            "talent_score": talent_score,
            "exposure_score": exposure_score,
            "opportunity_score": opportunity_score,
            "teg_status": teg_status
        }
    return teg_data

def extract_nlp_signals(open_ended_answers, api_key=None):
    indicators = {
        "curiosity": {"title": "Curiosity", "active": False, "evidence": ""},
        "self_awareness": {"title": "Self-awareness", "active": False, "evidence": ""},
        "problem_solving": {"title": "Problem-solving", "active": False, "evidence": ""},
        "imagination": {"title": "Imagination", "active": False, "evidence": ""},
        "leadership": {"title": "Leadership", "active": False, "evidence": ""},
        "emotional_intelligence": {"title": "Emotional intelligence", "active": False, "evidence": ""},
        "reflection": {"title": "Reflection", "active": False, "evidence": ""},
        "communication_style": {"title": "Communication style", "active": False, "evidence": ""},
    }
    
    combined_text = " ".join([v for v in open_ended_answers.values() if v]).strip()
    if not combined_text:
        return indicators

    if api_key:
        prompt = f"""
        You are an advanced educational AI psychometric analyst.
        Analyze these four open-ended responses written by a child:
        - What makes them lose track of time (Flow State): "{open_ended_answers.get("deep_discovery_flow", "")}"
        - Proudest achievement (Pride): "{open_ended_answers.get("deep_discovery_pride", "")}"
        - One-year learning quest (Curiosity): "{open_ended_answers.get("deep_discovery_curiosity", "")}"
        - Future problem solving vision (Vision): "{open_ended_answers.get("deep_discovery_vision", "")}"

        We are looking for evidence of 8 specific semantic indicators:
        1. curiosity: showing a love for learning, questioning, and exploring new ideas.
        2. self_awareness: understanding one's own feelings, strengths, or personal goals.
        3. problem_solving: showing logical approach, analytical interest, or desire to fix/solve things.
        4. imagination: showcasing creativity, drawing, writing, building, or divergent thinking.
        5. leadership: showing initiative to guide others, organize groups, or coordinate.
        6. emotional_intelligence: showing empathy, caring about others' feelings, or supporting peers.
        7. reflection: looking back at past achievements or learning from experiences.
        8. communication_style: expressiveness in writing, using rich explanation or narrative.

        Please respond with a raw JSON block only (no markdown, no formatting, no wrapper) containing:
        A dict mapping each key (curiosity, self_awareness, problem_solving, imagination, leadership, emotional_intelligence, reflection, communication_style) to an object with:
        - "active": boolean (true if there is clear evidence in the text, false otherwise)
        - "evidence": string (a concise quote or description of evidence from the child's text, e.g. "Expressed pride in 'making a cardboard game'")
        """
        try:
            res = call_gemini_api(prompt, api_key)
            if res and isinstance(res, dict):
                for key, val in res.items():
                    if key in indicators and isinstance(val, dict):
                        indicators[key]["active"] = bool(val.get("active", False))
                        indicators[key]["evidence"] = str(val.get("evidence", ""))
                return indicators
        except Exception as e:
            print(f"DEBUG: NLP Gemini analysis exception: {e}")
            
    lower_text = combined_text.lower()
    keywords_map = {
        "curiosity": {
            "en": ["learn", "explore", "ask", "why", "how", "wonder", "find", "read", "know", "discover", "science", "space", "stars", "coding", "history"],
            "hi": ["सीख", "जानना", "खोज", "पूछ", "क्यूं", "क्यों", "कैसे", "पता", "विज्ञान", "अंतरिक्ष", "तारे"]
        },
        "self_awareness": {
            "en": ["myself", "i feel", "happy", "proud", "my dream", "my goal", "improve", "like to", "personal"],
            "hi": ["सोच", "लगता", "महसूस", "खुश", "गर्व", "खुद", "सपना", "लक्ष्य", "पसंद"]
        },
        "problem_solving": {
            "en": ["solve", "fix", "repair", "code", "math", "problem", "puzzle", "reason", "logic", "mechanic", "engineer", "build a machine"],
            "hi": ["सुलझा", "ठीक", "हल", "समस्या", "गणित", "पहेली", "मशीन", "इंजीनियर"]
        },
        "imagination": {
            "en": ["build", "draw", "create", "paint", "make", "imagine", "invent", "story", "craft", "design", "art", "music", "sketch", "crafting"],
            "hi": ["बनाना", "चित्र", "रचना", "कहानी", "बनाऊं", "बनाऊ", "सृजन", "कल्पना", "कला", "संगीत", "रेखाचित्र"]
        },
        "leadership": {
            "en": ["lead", "guide", "organize", "captain", "direct", "head", "group project", "manage", "coordinate"],
            "hi": ["नेतृत्व", "मार्गदर्शन", "कैप्टन", "टीम", "निर्देशन", "लीड"]
        },
        "emotional_intelligence": {
            "en": ["friend", "help", "care", "feelings", "support", "understand", "kind", "family", "together", "share"],
            "hi": ["दोस्त", "मित्र", "मदद", "भावना", "समझ", "दया", "ख्याल", "परिवार", "साथ", "बांटना"]
        },
        "reflection": {
            "en": ["past", "completed", "remember", "learnt", "achieved", "learned", "succeeded", "won", "yesterday"],
            "hi": ["बीता", "याद", "सीखा", "सफलता", "जीता", "अतीत", "पहले"]
        },
        "communication_style": {
            "en": ["talk", "speak", "write", "explain", "tell", "express", "say", "debate", "speech", "english", "hindi", "language", "words"],
            "hi": ["बात", "बोल", "लिख", "बता", "कह", "भाषण", "वाद-विवाद", "भाषा", "शब्द"]
        }
    }

    def find_evidence_snippet(key, keywords_en, keywords_hi):
        for q_name, q_val in open_ended_answers.items():
            if not q_val:
                continue
            q_val_lower = q_val.lower()
            for kw in keywords_en + keywords_hi:
                if kw in q_val_lower:
                    idx = q_val_lower.find(kw)
                    start = max(0, idx - 15)
                    end = min(len(q_val), idx + len(kw) + 25)
                    snippet = q_val[start:end].strip()
                    source_label = {
                        "deep_discovery_flow": "Flow State",
                        "deep_discovery_pride": "Pride",
                        "deep_discovery_curiosity": "Curiosity",
                        "deep_discovery_vision": "Vision"
                    }.get(q_name, "discovery answers")
                    return f"Expressed in {source_label}: '...{snippet}...'"
        return ""

    for key, mapping in keywords_map.items():
        en_kw = mapping["en"]
        hi_kw = mapping["hi"]
        found = False
        for kw in en_kw + hi_kw:
            if kw in lower_text:
                found = True
                break
        if found:
            indicators[key]["active"] = True
            indicators[key]["evidence"] = find_evidence_snippet(key, en_kw, hi_kw)
            
    return indicators

def score_responses(responses, child, discovery_answers=None, facilitator_note=None, weights=None, past_sessions_count=0):
    """
    Core scoring engine.
    Computes Discovery (15%), Exposure (10%), Deep Assessment (60% / 75%), and Facilitator (15%) weights.
    Returns standard tq_scores, integrated, eq_score, visualizer_score, metrics, and new analytics.
    """
    if weights is None:
        weights = {
            "assessment": 0.60,
            "open_responses": 0.20,
            "facilitator": 0.20
        }
    
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

    # Combine with weights (Adjustable weights implementation)
    if not has_notes:
        w_assess = 0.80
        w_open = 0.20
        w_fac = 0.0
    else:
        w_assess = weights.get("assessment", 0.60)
        w_open = weights.get("open_responses", 0.20)
        w_fac = weights.get("facilitator", 0.20)

    # Calculate Open Responses score
    open_scores = {}
    flow_score = get_text_completion_score(responses.get("deep_discovery_flow"))
    pride_score = get_text_completion_score(responses.get("deep_discovery_pride"))
    curiosity_score = get_text_completion_score(responses.get("deep_discovery_curiosity"))
    vision_score = get_text_completion_score(responses.get("deep_discovery_vision"))
    avg_open_all = (flow_score + pride_score + curiosity_score + vision_score) / 4.0

    blended = {}
    for domain in DOMAIN_WEIGHTS.keys():
        s_disc = (discovery_counts.get(domain, 0) / 6.0) * 100.0
        s_exp = (child.get(f"exp_{domain}", 0) / 3.0) * 100.0
        s_deep = tq_raw_scores.get(domain, 0.0)
        s_fac = facilitator_scores[domain]
        
        # Domain-specific open score mapping
        if domain == "intrapersonal":
            s_open = (flow_score + pride_score + curiosity_score) / 3.0
        elif domain == "social":
            s_open = vision_score
        else:
            s_open = avg_open_all
            
        s_assess = 0.75 * s_deep + 0.15 * s_disc + 0.10 * s_exp
        blended[domain] = w_assess * s_assess + w_open * s_open + w_fac * s_fac

    # Wide stretch-normalization to prevent domain clustering (target 35 to 95)
    max_raw = max(blended.values())
    min_raw = min(blended.values())
    final_scores = {}
    if max_raw > min_raw:
        target_min = 35.0
        target_max = 95.0
        target_min = 35.0
        target_max = 95.0
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
    
    # 2. Response Consistency/accuracy (max 20 pts)
    metrics = extract_metric_summary(responses)
    accuracy_rate = metrics.get("accuracy_rate", 0.0) or 0.0
    consistency_pts = 20 if 0.4 <= accuracy_rate <= 0.85 else 10
    consistency_desc = "high accuracy and stable pacing" if consistency_pts == 20 else "varying response accuracy"
    
    # 3. Domain Separation (max 20 pts)
    avg_score = sum(final_scores.values()) / len(final_scores) if final_scores else 50
    separation_gap = final_scores.get(top_domain, 50) - avg_score
    separation_pts = 20 if separation_gap >= 12 else 10 if separation_gap >= 6 else 5
    separation_desc = "strong separation between domains" if separation_gap >= 12 else "moderate domain differentiation"
    
    # 4. Facilitator note validation status (max 15 pts)
    fac_validation_pts = 15 if facilitator_note is not None else 0
    
    # 5. Repeated assessment count (max 15 pts)
    repeated_pts = 15 if past_sessions_count >= 2 else 10 if past_sessions_count == 1 else 0

    confidence_score = task_pts + consistency_pts + separation_pts + fac_validation_pts + repeated_pts
    
    # Map confidence to levels
    if confidence_score >= 85:
        confidence_level = "Very High"
    elif confidence_score >= 70:
        confidence_level = "High"
    elif confidence_score >= 50:
        confidence_level = "Moderate"
    else:
        confidence_level = "Low"

    confidence_desc = (
        f"Confidence is {confidence_level} ({confidence_score}/100) because {tasks_answered} interactive tasks "
        f"were completed, the child demonstrated {consistency_desc}, and their scores showed {separation_desc}."
    )

    # Expose evidence sources
    combined_res = {**(discovery_answers or {}), **responses}
    has_open_ended = any(len(str(combined_res.get(k, "") or "")) > 0 for k in ["deep_discovery_flow", "deep_discovery_pride", "deep_discovery_curiosity", "deep_discovery_vision"])
    
    evidence_sources = {
        "assessment_responses": tasks_answered > 0,
        "open_ended_answers": has_open_ended,
        "facilitator_validation": facilitator_note is not None,
        "repeated_assessments": past_sessions_count > 0
    }

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

    # Compute GTI and TEG
    gti_score, gti_label = calculate_gti(sorted_domains)
    teg_data = calculate_teg(final_scores, child)

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
        "evidence_sources": evidence_sources,
        "gti_score": gti_score,
        "gti_label": gti_label,
        "teg_data": teg_data,
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
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    if role == "master_admin":
        rows = db.execute("SELECT id, name, email, role, active, center_id, organization_id FROM users").fetchall()
    else:
        rows = db.execute("SELECT id, name, email, role, active, center_id, organization_id FROM users WHERE organization_id = ?", (org_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/users", methods=["POST"])
@require_role(["master_admin", "admin"])
def create_user_tms():
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    user_org_id = user.get("organization_id")
    
    data = request.json or {}
    name = data.get("name")
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    user_role = data.get("role", "facilitator")
    center_id = data.get("center_id")
    
    db = get_db()
    if role == "master_admin":
        org_id = data.get("organization_id") or 1
    else:
        org_id = user_org_id
        # Also ensure that if they specify a center_id, it belongs to their organization
        if center_id:
            center = db.execute("SELECT organization_id FROM centers WHERE id = ?", (center_id,)).fetchone()
            if not center or center["organization_id"] != user_org_id:
                return jsonify({"error": "Forbidden: Center belongs to another organization"}), 403

    if not name or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
        
    try:
        db.execute("""
            INSERT INTO users (name, email, password_hash, role, organization_id, center_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, hash_password(password), user_role, org_id, center_id))
        db.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"status": "success"}), 201

@app.route("/api/admin/users/<uid>", methods=["DELETE"])
@require_role(["master_admin", "admin"])
def delete_user_tms(uid):
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    # Check if the target user belongs to same org
    target_user = db.execute("SELECT organization_id FROM users WHERE id=?", (uid,)).fetchone()
    if not target_user:
        return jsonify({"error": "User not found"}), 404
        
    if role != "master_admin":
        if target_user["organization_id"] != org_id:
            return jsonify({"error": "Forbidden: User belongs to another organization"}), 403
            
    db.execute("DELETE FROM users WHERE id=?", (uid,))
    db.commit()
    return jsonify({"status": "success"})

@app.route("/api/admin/users/<uid>/approve", methods=["PUT"])
@require_role(["master_admin", "admin"])
def approve_user_tms(uid):
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    user_row = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not user_row:
        return jsonify({"error": "User not found"}), 404
        
    if role != "master_admin":
        if user_row["organization_id"] != org_id:
            return jsonify({"error": "Forbidden: User belongs to another organization"}), 403

    data = request.json or {}
    approved_role = data.get("role")
    center_id = data.get("center_id")
    
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
            # check center org
            center = db.execute("SELECT organization_id FROM centers WHERE id = ?", (center_id,)).fetchone()
            if role != "master_admin" and (not center or center["organization_id"] != org_id):
                return jsonify({"error": "Forbidden: Center belongs to another organization"}), 403
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
                sp_client.table("profiles").update({"role": approved_role, "is_approved": True}).eq("email", user_row["email"]).execute()
                print(f"[SUPABASE SYNC] Approved user role {approved_role} for {user_row['email']}")
            except Exception as e:
                print(f"[SUPABASE WARNING] Failed to sync approved user role: {e}")
    except Exception as e:
        return jsonify({"error": str(e)}), 400
        
    return jsonify({"status": "success", "role": approved_role})

# ── PUBLIC ENDPOINTS (NO AUTH REQUIRED) ──────────────────────────────────────
@app.route("/api/public/centers", methods=["GET"])
def list_public_centers():
    db = get_db()
    rows = db.execute("SELECT id, name FROM centers ORDER BY id ASC").fetchall()
    return jsonify([dict(r) for r in rows])

# ── CENTER MANAGEMENT ENDPOINTS ─────────────────────────────────────────────
@app.route("/api/centers", methods=["GET"])
def list_centers():
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    if role == "master_admin":
        rows = db.execute("SELECT * FROM centers").fetchall()
    else:
        rows = db.execute("SELECT * FROM centers WHERE organization_id = ?", (org_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/centers", methods=["POST"])
@require_role(["master_admin", "admin"])
def create_center():
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    user_org_id = user.get("organization_id")
    
    data = request.json or {}
    name = data.get("name")
    location = data.get("location")
    if not name:
        return jsonify({"error": "Center name required"}), 400
        
    if role == "master_admin":
        org_id = data.get("organization_id") or 1
    else:
        org_id = user_org_id
        
    db = get_db()
    db.execute("INSERT INTO centers (name, location, organization_id) VALUES (?, ?, ?)", (name, location, org_id))
    db.commit()
    return jsonify({"status": "success"}), 201

# ── WORKSHOP PLANNING & ATTENDANCE ──────────────────────────────────────────
@app.route("/api/workshops", methods=["GET"])
def list_workshops():
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    if role == "master_admin":
        rows = db.execute("SELECT w.*, c.name as center_name FROM workshops w LEFT JOIN centers c ON c.id=w.center_id").fetchall()
    else:
        rows = db.execute("SELECT w.*, c.name as center_name FROM workshops w LEFT JOIN centers c ON c.id=w.center_id WHERE w.organization_id = ?", (org_id,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/workshops", methods=["POST"])
@require_role(["master_admin", "admin"])
def create_workshop():
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    user_org_id = user.get("organization_id")
    
    data = request.json or {}
    name = data.get("name")
    domain = data.get("domain")
    center_id = data.get("center_id")
    description = data.get("description")
    if not name or not domain:
        return jsonify({"error": "Name and domain are required"}), 400
        
    db = get_db()
    if role == "master_admin":
        org_id = data.get("organization_id") or 1
        if center_id:
            center = db.execute("SELECT organization_id FROM centers WHERE id = ?", (center_id,)).fetchone()
            if center:
                org_id = center["organization_id"]
    else:
        org_id = user_org_id
        if center_id:
            center = db.execute("SELECT organization_id FROM centers WHERE id = ?", (center_id,)).fetchone()
            if not center or center["organization_id"] != user_org_id:
                return jsonify({"error": "Forbidden: Center belongs to another organization"}), 403
                
    db.execute("INSERT INTO workshops (name, domain, center_id, organization_id, description) VALUES (?, ?, ?, ?, ?)", (name, domain, center_id, org_id, description))
    db.commit()
    return jsonify({"status": "success"}), 201

@app.route("/api/workshops/<int:wid>/sessions", methods=["GET"])
def list_workshop_sessions(wid):
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    workshop = db.execute("SELECT organization_id FROM workshops WHERE id = ?", (wid,)).fetchone()
    if not workshop:
        return jsonify({"error": "Workshop not found"}), 404
        
    if role != "master_admin" and workshop["organization_id"] != org_id:
        return jsonify({"error": "Forbidden: Workshop belongs to another organization"}), 403
        
    rows = db.execute("SELECT * FROM workshop_sessions WHERE workshop_id=?", (wid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/workshops/<int:wid>/sessions", methods=["POST"])
@require_role(["master_admin", "admin", "mentor"])
def create_workshop_session(wid):
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    workshop = db.execute("SELECT organization_id FROM workshops WHERE id = ?", (wid,)).fetchone()
    if not workshop:
        return jsonify({"error": "Workshop not found"}), 404
        
    if role != "master_admin" and workshop["organization_id"] != org_id:
        return jsonify({"error": "Forbidden: Workshop belongs to another organization"}), 403
        
    data = request.json or {}
    session_date = data.get("session_date")
    notes = data.get("notes")
    attendance = data.get("attendance", {})
    
    if not session_date:
        return jsonify({"error": "Session date required"}), 400
        
    cur = db.execute("INSERT INTO workshop_sessions (workshop_id, session_date, notes) VALUES (?, ?, ?)", (wid, session_date, notes))
    session_id = cur.lastrowid
    
    for cid_str, status in attendance.items():
        try:
            cid = int(cid_str)
            child = db.execute("SELECT organization_id FROM children WHERE id = ?", (cid,)).fetchone()
            if child and (role == "master_admin" or child["organization_id"] == org_id):
                db.execute("INSERT INTO workshop_attendance (workshop_session_id, child_id, status) VALUES (?, ?, ?)", (session_id, cid, status))
        except Exception:
            pass
            
    db.commit()
    return jsonify({"status": "success", "session_id": session_id}), 201

@app.route("/api/workshops/attendance/<int:cid>", methods=["GET"])
def list_student_attendance(cid):
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    child = db.execute("SELECT organization_id, center_id FROM children WHERE id=?", (cid,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    if role != "master_admin":
        if child["organization_id"] != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child["center_id"] != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
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
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    child = db.execute("SELECT organization_id, center_id FROM children WHERE id=?", (cid,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    if role != "master_admin":
        if child["organization_id"] != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child["center_id"] != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
    rows = db.execute("SELECT * FROM mentor_validations WHERE child_id=? ORDER BY created_at DESC", (cid,)).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/mentors/validations", methods=["POST"])
@require_role(["master_admin", "admin", "mentor"])
def submit_mentor_validation():
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
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
    child = db.execute("SELECT organization_id, center_id FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
        
    if role != "master_admin":
        if child["organization_id"] != org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if role != "admin" and child["center_id"] != center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
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
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    center_id = user.get("center_id")
    
    db = get_db()
    
    # 1. Talent Distribution query
    if role == "master_admin":
        sessions = db.execute("SELECT top_domain, COUNT(*) as cnt FROM sessions WHERE status='complete' GROUP BY top_domain").fetchall()
    elif role == "admin":
        sessions = db.execute("""
            SELECT s.top_domain, COUNT(*) as cnt 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=?
            GROUP BY s.top_domain
        """, (org_id,)).fetchall()
    else:
        sessions = db.execute("""
            SELECT s.top_domain, COUNT(*) as cnt 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
            GROUP BY s.top_domain
        """, (org_id, center_id)).fetchall()
    talent_dist = {r["top_domain"]: r["cnt"] for r in sessions if r["top_domain"]}
    
    # 2. Workshop demand query
    if role == "master_admin":
        workshops = db.execute("SELECT domain, COUNT(*) as cnt FROM workshops GROUP BY domain").fetchall()
    elif role == "admin":
        workshops = db.execute("""
            SELECT domain, COUNT(*) as cnt 
            FROM workshops 
            WHERE organization_id=? 
            GROUP BY domain
        """, (org_id,)).fetchall()
    else:
        workshops = db.execute("""
            SELECT domain, COUNT(*) as cnt 
            FROM workshops 
            WHERE organization_id=? AND center_id=? 
            GROUP BY domain
        """, (org_id, center_id)).fetchall()
    workshop_demand = {r["domain"]: r["cnt"] for r in workshops if r["domain"]}
    
    # 3. Untapped potential query
    if role == "master_admin":
        sessions_all = db.execute("SELECT child_id, personality_data FROM sessions WHERE status='complete'").fetchall()
    elif role == "admin":
        sessions_all = db.execute("""
            SELECT s.child_id, s.personality_data 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=?
        """, (org_id,)).fetchall()
    else:
        sessions_all = db.execute("""
            SELECT s.child_id, s.personality_data 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
        """, (org_id, center_id)).fetchall()
        
    untapped_counts = {}
    for s in sessions_all:
        try:
            pdata = json.loads(s["personality_data"] or "{}")
            untapped = pdata.get("untapped_potential", [])
            for u in untapped:
                untapped_counts[u] = untapped_counts.get(u, 0) + 1
        except Exception:
            pass
            
    # 4. Growth data query
    if role == "master_admin":
        growth_rows = db.execute("SELECT top_domain, tq_scores, completed_at FROM sessions WHERE status='complete' ORDER BY completed_at").fetchall()
    elif role == "admin":
        growth_rows = db.execute("""
            SELECT s.top_domain, s.tq_scores, s.completed_at 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=?
            ORDER BY s.completed_at
        """, (org_id,)).fetchall()
    else:
        growth_rows = db.execute("""
            SELECT s.top_domain, s.tq_scores, s.completed_at 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
            ORDER BY s.completed_at
        """, (org_id, center_id)).fetchall()
        
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
            
    # 5. Funnel query totals
    if role == "master_admin":
        total_registered = db.execute("SELECT COUNT(*) FROM children").fetchone()[0]
        total_assessed = db.execute("SELECT COUNT(DISTINCT child_id) FROM sessions WHERE status='complete'").fetchone()[0]
        total_matched = db.execute("SELECT COUNT(*) FROM mentor_matches WHERE status='active'").fetchone()[0]
        total_enrolled = db.execute("SELECT COUNT(DISTINCT child_id) FROM workshop_attendance WHERE status='Present'").fetchone()[0]
    elif role == "admin":
        total_registered = db.execute("SELECT COUNT(*) FROM children WHERE organization_id=?", (org_id,)).fetchone()[0]
        total_assessed = db.execute("""
            SELECT COUNT(DISTINCT s.child_id) 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=?
        """, (org_id,)).fetchone()[0]
        total_matched = db.execute("""
            SELECT COUNT(*) 
            FROM mentor_matches mm
            JOIN children c ON mm.child_id = c.id
            WHERE mm.status='active' AND c.organization_id=?
        """, (org_id,)).fetchone()[0]
        total_enrolled = db.execute("""
            SELECT COUNT(DISTINCT a.child_id) 
            FROM workshop_attendance a
            JOIN children c ON a.child_id = c.id
            WHERE a.status='Present' AND c.organization_id=?
        """, (org_id,)).fetchone()[0]
    else:
        total_registered = db.execute("SELECT COUNT(*) FROM children WHERE organization_id=? AND center_id=?", (org_id, center_id)).fetchone()[0]
        total_assessed = db.execute("""
            SELECT COUNT(DISTINCT s.child_id) 
            FROM sessions s
            JOIN children c ON s.child_id = c.id
            WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
        """, (org_id, center_id)).fetchone()[0]
        total_matched = db.execute("""
            SELECT COUNT(*) 
            FROM mentor_matches mm
            JOIN children c ON mm.child_id = c.id
            WHERE mm.status='active' AND c.organization_id=? AND c.center_id=?
        """, (org_id, center_id)).fetchone()[0]
        total_enrolled = db.execute("""
            SELECT COUNT(DISTINCT a.child_id) 
            FROM workshop_attendance a
            JOIN children c ON a.child_id = c.id
            WHERE a.status='Present' AND c.organization_id=? AND c.center_id=?
        """, (org_id, center_id)).fetchone()[0]
        
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
    user, error = require_user()
    if error:
        return error
    role = user.get("role")
    org_id = user.get("organization_id")
    
    db = get_db()
    
    if role == "master_admin":
        children = db.execute("SELECT * FROM children").fetchall()
    else:
        children = db.execute("SELECT * FROM children WHERE organization_id=?", (org_id,)).fetchall()
        
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
        headers={"Content-disposition": "attachment; filename=GOAT_Talent_Export.csv"}
    )


@app.route("/api/sessions/<int:sid>/pdf", methods=["GET"])
def export_session_pdf(sid):
    # 1. Verification of the token (allow token in headers or query params)
    token = request.args.get("token")
    user = None
    if token:
        try:
            sb_user_resp = supabase.auth.get_user(token)
            if sb_user_resp and sb_user_resp.user:
                email = sb_user_resp.user.email
                db = get_db()
                row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                if row:
                    user = dict(row)
                else:
                    role, org, center = resolve_user_profile(email, getattr(sb_user_resp.user, 'user_metadata', {}) or {})
                    user = {
                        "id": sb_user_resp.user.id,
                        "email": email,
                        "role": role,
                        "organization_id": org,
                        "center_id": center
                    }
        except Exception as e:
            print(f"[AUTH WARNING] Failed to verify Supabase token for PDF: {e}")
            
    if not user:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token_h = auth.replace("Bearer ", "", 1).strip()
            try:
                sb_user_resp = supabase.auth.get_user(token_h)
                if sb_user_resp and sb_user_resp.user:
                    email = sb_user_resp.user.email
                    db = get_db()
                    row = db.execute("SELECT id, name, email, role, organization_id, center_id FROM users WHERE email=?", (email,)).fetchone()
                    if row:
                        user = dict(row)
                    else:
                        role, org, center = resolve_user_profile(email, getattr(sb_user_resp.user, 'user_metadata', {}) or {})
                        user = {
                            "id": sb_user_resp.user.id,
                            "email": email,
                            "role": role,
                            "organization_id": org,
                            "center_id": center
                        }
            except Exception as e:
                pass
                
    if not user:
        # Check fallback local session check
        if token:
            row = get_db().execute("""
                SELECT u.id, u.name, u.email, u.role, u.organization_id, u.center_id
                FROM auth_sessions s
                JOIN users u ON u.id = s.user_id
                WHERE s.token = ? AND s.expires_at > datetime('now')
            """, (token,)).fetchone()
            if row:
                user = dict(row)
                
    if not user:
        return jsonify({"error": "Unauthorized. A valid token is required to download this report."}), 401
        
    db = get_db()
    session_row = db.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
    if not session_row:
        return jsonify({"error": "Session not found"}), 404
    session = dict(session_row)
        
    child_row = db.execute("SELECT * FROM children WHERE id=?", (session["child_id"],)).fetchone()
    if not child_row:
        return jsonify({"error": "Child not found"}), 404
    child = dict(child_row)
        
    # Scope check
    user_role = user.get("role")
    user_org_id = user.get("organization_id")
    user_center_id = user.get("center_id")
    
    if user_role != "master_admin":
        if child.get("organization_id") != user_org_id:
            return jsonify({"error": "Forbidden: Child belongs to another organization"}), 403
        if user_role != "admin" and child.get("center_id") != user_center_id:
            return jsonify({"error": "Forbidden: Child belongs to another center"}), 403
            
    # 2. Setup ReportLab PDF document in memory
    import io
    import math
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.shapes import Drawing, Polygon, Line, Circle, String, Group, Rect
    
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
    )
    
    # Premium Style Palette
    primary_color = colors.HexColor("#5B4CF0")    # Indigo
    secondary_color = colors.HexColor("#00B8A9")  # Teal
    text_color = colors.HexColor("#2D3436")       # Dark Charcoal
    light_bg = colors.HexColor("#F8F9FA")         # Light Grey
    border_color = colors.HexColor("#E2E8F0")     # Light Border
    accent_gold = colors.HexColor("#F7B731")      # Gold
    
    # Typography Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=primary_color,
        spaceAfter=15,
        alignment=1 # Center
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceBefore=5,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_color,
        spaceAfter=10
    )
    
    italic_style = ParagraphStyle(
        'ReportItalic',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor("#4A4A4A")
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=secondary_color,
        spaceAfter=4,
        textTransform='uppercase'
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=text_color
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    card_label_style = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=primary_color
    )

    card_body_style = ParagraphStyle(
        'CardBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=text_color
    )
    
    # Static Data Maps
    DOMAINS_MAP = {
        "kinesthetic": "Kinesthetic & Physical",
        "creative": "Creative & Artistic",
        "logical": "Logical & Analytical",
        "spatial": "Spatial & Making",
        "social": "Social & Leadership",
        "language": "Language & Communication",
        "naturalist": "Naturalist & Environmental",
        "intrapersonal": "Intrapersonal & Reflective"
    }

    DOMAIN_COLORS = {
        "kinesthetic": colors.HexColor("#FF7675"),
        "creative": colors.HexColor("#6C5CE7"),
        "logical": colors.HexColor("#0984E3"),
        "spatial": colors.HexColor("#FD9644"),
        "social": colors.HexColor("#00B894"),
        "language": colors.HexColor("#D63031"),
        "naturalist": colors.HexColor("#26DE81"),
        "intrapersonal": colors.HexColor("#A55EEA")
    }

    PERSONAS = {
        "creative": {
            "title": "THE CREATOR",
            "emoji": "🎨",
            "desc": "This child enjoys generating original ideas, imagining possibilities, and expressing thoughts through visual and artistic mediums.",
            "strengths": ["Vivid Imagination", "Divergent Thinking", "Original Expression"],
            "growth": ["Structured Completion", "Attention to Rote Rules"]
        },
        "spatial": {
            "title": "THE BUILDER",
            "emoji": "🔧",
            "desc": "This child thinks in three dimensions, loves constructing physical or mental models, and naturally understands design structures.",
            "strengths": ["3D Visualization", "Structural Logic", "Spatial Transformation"],
            "growth": ["Verbalizing Concepts", "Patience with Abstract Theory"]
        },
        "logical": {
            "title": "THE THINKER",
            "emoji": "🧠",
            "desc": "This child is highly analytical, naturally notices logical patterns, loves solving puzzles, and thrives on structured reasoning.",
            "strengths": ["Pattern Recognition", "Reasoning & Logic", "Systematic Problem-Solving"],
            "growth": ["Handling Vague Goals", "Accepting Open-Ended Ambiguity"]
        },
        "social": {
            "title": "THE LEADER",
            "emoji": "🤝",
            "desc": "This child possesses natural social intelligence, easily connects with others, coordinates collaborative activities, and guides groups.",
            "strengths": ["Empathy & Influence", "Group Organization", "Collaborative Coordination"],
            "growth": ["Delegating Tasks", "Sustaining Quiet Focus"]
        },
        "language": {
            "title": "THE COMMUNICATOR",
            "emoji": "💬",
            "desc": "This child has a natural affinity for words, excels in verbal storytelling, expresses ideas with high clarity, and loves debate.",
            "strengths": ["Verbal Fluency", "Narrative Structure", "Persuasive Explanation"],
            "growth": ["Listening Without Interrupting", "Silent Individual Practice"]
        },
        "naturalist": {
            "title": "THE OBSERVER",
            "emoji": "🌱",
            "desc": "This child has unusual detail-awareness in nature, notices micro-patterns in ecosystems, and loves classifying biological details.",
            "strengths": ["Sensory Observation", "Taxonomic Classification", "Environmental Empathy"],
            "growth": ["Abstract Symbolic Tasks", "Prolonged Desk-Bound Study"]
        },
        "kinesthetic": {
            "title": "THE EXPLORER",
            "emoji": "🏃",
            "desc": "This child learns best through physical doing, movement, and hands-on trial-and-error, demonstrating great fine-motor control.",
            "strengths": ["Fine-Motor Precision", "Coordination & Agility", "Kinesthetic Intuition"],
            "growth": ["Passive Auditory Learning", "Prolonged Sitting Work"]
        },
        "intrapersonal": {
            "title": "THE RESEARCHER",
            "emoji": "🧘",
            "desc": "This child exhibits deep self-awareness, prefers reflecting in quiet spaces, understands personal motivations, and sets thoughtful goals.",
            "strengths": ["Emotional Reflexivity", "Independent Planning", "Goal-Oriented Perseverance"],
            "growth": ["Highly Competitive Groups", "Spontaneous Public Speaking"]
        }
    }

    parentGuides = {
        "creative": {
            "behaviors": ["Imagines highly unusual possibilities", "Enjoys open-ended tasks and abstract games", "Prefers visual creation over pure memorization"],
            "motivators": "Original expression, visual challenges, autonomy in choices",
            "styles": "Divergent and visual-first",
            "challenges": "Can easily become bored by highly repetitive or rigid work",
            "support": ["Provide diverse physical and digital design materials", "Allow space for experimentation without immediate grading"]
        },
        "spatial": {
            "behaviors": ["Likes physical construction and model-building", "Enjoys visualizing shapes and three-dimensional blocks", "Notices minute structural details in drawings"],
            "motivators": "Building, assembling, transforming structures, design tasks",
            "styles": "Three-dimensional and hands-on",
            "challenges": "May sometimes struggle to explain spatial concepts in written text",
            "support": ["Encourage model building and tinkering workshops", "Use visual diagrams and physical models for academic study"]
        },
        "logical": {
            "behaviors": ["Enjoys solving complex riddles and puzzles", "Notices mathematical patterns spontaneously", "Structures thoughts sequentially and logically"],
            "motivators": "Systematic patterns, numerical puzzles, clear cause-and-effect rules",
            "styles": "Analytical, sequence-based",
            "challenges": "May get frustrated by vague directions or emotional debates",
            "support": ["Provide math puzzles and logic-based board games", "Structure daily tasks with clear sequences and logical rules"]
        },
        "social": {
            "behaviors": ["Naturally organizes peers and group activities", "Shows high empathy and notices others' emotions", "Takes active initiative in coordinating events"],
            "motivators": "Collaborative projects, peer coordination, group problem-solving",
            "styles": "Interpersonal, leadership-driven",
            "challenges": "May dominate discussions or take on too much responsibility",
            "support": ["Provide leadership opportunities with guidance on delegation", "Encourage group games that require active listening and compromise"]
        },
        "language": {
            "behaviors": ["Expresses thoughts with high verbal clarity", "Enjoys telling stories and describing scenarios", "Has an extensive vocabulary and notices wordplay"],
            "motivators": "Debate, verbal explanation, storytelling, theater performance",
            "styles": "Verbal-auditory, narrative-driven",
            "challenges": "May talk excessively or struggle with silent, individual tasks",
            "support": ["Encourage storytelling, theater, or writing workshops", "Discuss complex topics together to challenge verbal expression"]
        },
        "naturalist": {
            "behaviors": ["Notices details in plants, animals, and ecosystems", "Loves sorting, classifying, and organizing collections", "Shows deep empathy and interest in the natural world"],
            "motivators": "Outdoor observations, wildlife exploration, environmental projects",
            "styles": "Environmental-observational",
            "challenges": "May get restless in closed, sedentary indoor spaces",
            "support": ["Provide opportunities for regular nature exploration", "Use outdoor settings and animal themes for academic concepts"]
        },
        "kinesthetic": {
            "behaviors": ["Demonstrates exceptional coordination and motor speed", "Learns concepts best by physically doing or moving", "Has strong fine-motor skills and tactile intuition"],
            "motivators": "Physical movement, sports, hands-on construction, active games",
            "styles": "Tactile-physical, experimental",
            "challenges": "Needs regular physical breaks; may fidget in quiet lectures",
            "support": ["Integrate physical movement and breaks into study routines", "Encourage sports, dance, or hands-on crafting workshops"]
        },
        "intrapersonal": {
            "behaviors": ["Shows deep reflection and self-awareness of feelings", "Sets thoughtful personal goals and plans ahead", "Thrives when working independently on projects"],
            "motivators": "Solo hobbies, personal reflection, self-directed goals",
            "styles": "Reflective, self-guided",
            "challenges": "May withdraw during highly competitive or chaotic group work",
            "support": ["Provide quiet spaces for reflection and independent projects", "Encourage journaling or writing to process thoughts and emotions"]
        }
    }

    # Radar Chart Generator Flowable
    def draw_radar_chart(scores, width=504, height=220):
        cx = width / 2.0
        cy = height / 2.0
        r_max = 80.0
        
        d = Drawing(width, height)
        
        domains = [
            {"key": "creative", "label": "Creative & Artistic"},
            {"key": "spatial", "label": "Spatial & Making"},
            {"key": "language", "label": "Communication"},
            {"key": "social", "label": "Leadership & Social Impact"},
            {"key": "logical", "label": "Logical & Analytical"},
            {"key": "naturalist", "label": "Naturalist"},
            {"key": "kinesthetic", "label": "Kinesthetic"},
            {"key": "intrapersonal", "label": "Intrapersonal"},
        ]
        
        num_domains = len(domains)
        
        def get_coords(idx, value):
            angle = (idx * 2 * math.pi) / num_domains - math.pi / 2
            dist = (value / 100.0) * r_max
            return cx + dist * math.cos(angle), cy + dist * math.sin(angle)
            
        # Draw concentric grid lines (20%, 40%, 60%, 80%, 100%)
        for g in [20, 40, 60, 80, 100]:
            pts = []
            for i in range(num_domains):
                x, y = get_coords(i, g)
                pts.append(x)
                pts.append(y)
            d.add(Polygon(pts, strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.75, fillColor=None))
            
        # Draw axes lines from center to 100%
        for i in range(num_domains):
            x, y = get_coords(i, 100)
            d.add(Line(cx, cy, x, y, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.75))
            
        # Draw score polygon
        score_pts = []
        for i, dom in enumerate(domains):
            score = scores.get(dom["key"], 0)
            x, y = get_coords(i, score)
            score_pts.append(x)
            score_pts.append(y)
            
        d.add(Polygon(score_pts, fillColor=colors.HexColor("#5B4CF026"), strokeColor=colors.HexColor("#5B4CF0"), strokeWidth=2.0))
        
        # Draw score vertices
        for i, dom in enumerate(domains):
            score = scores.get(dom["key"], 0)
            x, y = get_coords(i, score)
            d.add(Circle(x, y, 3.5, fillColor=colors.HexColor("#FDCB6E"), strokeColor=colors.HexColor("#5B4CF0"), strokeWidth=1.2))
            
        # Draw labels
        for i, dom in enumerate(domains):
            x, y = get_coords(i, 118)
            lbl = dom["label"]
            
            anchor = "middle"
            if x < cx - 15:
                anchor = "end"
            elif x > cx + 15:
                anchor = "start"
                
            s = String(x, y - 2.5, lbl, fontName="Helvetica-Bold", fontSize=7.5, textAnchor=anchor, fillColor=colors.HexColor("#4A4A4A"))
            d.add(s)
            
        return d
        
    # Safely convert dates in python
    created_val = session["completed_at"] or session["created_at"]
    try:
        if isinstance(created_val, str):
            if "." in created_val:
                created_val = created_val.split(".")[0]
            if "T" in created_val:
                dt = datetime.strptime(created_val, "%Y-%m-%dT%H:%M:%S")
            else:
                dt = datetime.strptime(created_val, "%Y-%m-%d %H:%M:%S")
        else:
            dt = created_val
        formatted_date = dt.strftime("%B %d, %Y")
    except Exception:
        formatted_date = str(created_val)[:10]

    # Parse integrated scores & personality data
    integ = {}
    if session["integrated_score"]:
        try:
            integ = json.loads(session["integrated_score"])
        except Exception:
            pass
            
    analysis = {}
    if session["personality_data"]:
        try:
            analysis = json.loads(session["personality_data"])
        except Exception:
            pass
            
    sorted_scores = sorted(integ.items(), key=lambda x: x[1], reverse=True)
    primary_domain = analysis.get("primary_domain") or (sorted_scores[0][0] if sorted_scores else "creative")
    secondary_domains = analysis.get("secondary_domains") or [x[0] for x in sorted_scores[1:3]] or []
    emerging_domains = analysis.get("emerging_domains") or [x[0] for x in sorted_scores[3:6]] or []
    untapped_potential = analysis.get("untapped_potential") or []
    evidence = analysis.get("evidence") or {}
    
    primary_label = DOMAINS_MAP.get(primary_domain, primary_domain)
    
    # Query facilitator reviews
    notes_arr = db.execute("SELECT * FROM facilitator_notes WHERE session_id=? ORDER BY created_at DESC", (sid,)).fetchall()
    note = dict(notes_arr[0]) if notes_arr else {}
    facilitator_name = note.get("facilitator") or "GOAT Facilitator"

    # Query history for growth timeline
    history_rows = db.execute("SELECT id, created_at, completed_at, top_domain, integrated_score FROM sessions WHERE child_id=? AND (status='complete' OR phase='complete') ORDER BY created_at ASC", (session["child_id"],)).fetchall()
    history = [dict(row) for row in history_rows]

    # Personalized snapshot narrative fallback
    personalizedSnapshot = analysis.get("talent_narrative")
    if not personalizedSnapshot:
        sec_labels = [DOMAINS_MAP.get(d, d) for d in secondary_domains]
        sec_str = " and ".join(sec_labels) if sec_labels else "other areas"
        personalizedSnapshot = (
            f"{child.get('name', 'The student')} appears to demonstrate strong developmental indicators in {primary_label} "
            f"activities, suggests a natural comfort with {primary_label} concepts. "
            f"Secondary indicators also suggest potential in {sec_str} areas. Nurturing these talents in structured settings "
            f"will provide a clearer picture of their long-term growth."
        )

    story = []
    
    # ──────────────────────────────────────────────────────────
    # PAGE 1: COVER PAGE (Drawn in background callback)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 1)) # dummy flowable
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 2: CHILD SNAPSHOT & TALENT SUMMARY
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Child Snapshot", section_header_style))
    story.append(Paragraph("WHO IS THIS CHILD?", h1_style))
    story.append(Paragraph(f'"{personalizedSnapshot}"', italic_style))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("TALENT DOMAIN SUMMARY", h2_style))
    
    # Primary Domain Card
    t1 = Table([[
        Paragraph("<font color='#5B4CF0'><b>STRONG INDICATORS</b></font>", styles['Normal']),
    ], [
        Paragraph(f"<b>{primary_label.upper()}</b>", styles['Heading3']),
    ]], colWidths=[7.0 * inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEEDFE")),
        ('LINELEFT', (0,0), (0,-1), 5, colors.HexColor("#5B4CF0")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t1)
    story.append(Spacer(1, 12))
    
    # Secondary Domains Card
    secondary_labels = "  |  ".join([DOMAINS_MAP.get(d, d).upper() for d in secondary_domains])
    t2 = Table([[
        Paragraph("<font color='#00B8A9'><b>EMERGING INDICATORS</b></font>", styles['Normal']),
    ], [
        Paragraph(f"<b>{secondary_labels or 'NONE DETECTED'}</b>", styles['Heading4']),
    ]], colWidths=[7.0 * inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
        ('LINELEFT', (0,0), (0,-1), 5, colors.HexColor("#00B8A9")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t2)
    story.append(Spacer(1, 12))
    
    # Emerging Domains Card
    emerging_labels = "  |  ".join([DOMAINS_MAP.get(d, d).upper() for d in emerging_domains])
    t3 = Table([[
        Paragraph("<font color='#B7791F'><b>NEEDS FURTHER EXPLORATION</b></font>", styles['Normal']),
    ], [
        Paragraph(f"<b>{emerging_labels or 'NONE DETECTED'}</b>", styles['Heading4']),
    ]], colWidths=[7.0 * inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('LINELEFT', (0,0), (0,-1), 5, colors.HexColor("#F7B731")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t3)
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 3: PSYCHOLOGICAL TALENT MAP (RADAR CHART)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Psychological Talent Map", section_header_style))
    story.append(Paragraph("DYNAMIC COGNITIVE MAP", h1_style))
    story.append(Paragraph("This radar chart illustrates the student's strengths across the 8 core cognitive domains. The normalized indices indicate natural preferences rather than fixed ability levels.", body_style))
    
    chart_flowable = draw_radar_chart(integ, width=504, height=220)
    story.append(chart_flowable)
    story.append(Spacer(1, 15))
    
    # Score Table
    table_data = [[
        Paragraph("Domain", table_header_style),
        Paragraph("Strength Tier", table_header_style),
        Paragraph("Developmental Wording", table_header_style)
    ]]
    
    # Display top 5 sorted domains
    for d_key, val in sorted_scores[:5]:
        lbl = DOMAINS_MAP.get(d_key, d_key)
        # Interpretation logic
        if val >= 75:
            tier = "<font color='#5B4CF0'><b>Strong Indicators</b></font>"
            desc = "Demonstrates consistent, highly accurate pattern execution and rapid responses."
        elif val >= 50:
            tier = "<font color='#00B8A9'><b>Emerging Indicators</b></font>"
            desc = "Suggests solid foundational capability; demonstrates intuitive comfort but requires further practice."
        else:
            tier = "<font color='#8E9BAE'><b>Needs Validation</b></font>"
            desc = "Represents an area with limited spontaneous indicators; would benefit from introductory exposure."
            
        table_data.append([
            Paragraph(f"<b>{lbl}</b>", table_cell_style),
            Paragraph(tier, table_cell_style),
            Paragraph(desc, table_cell_style)
        ])
        
    scores_table = Table(table_data, colWidths=[2.2 * inch, 1.5 * inch, 3.3 * inch])
    scores_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(scores_table)
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 4: EVIDENCE REPORT (WHY THESE RESULTS?)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Evidence Report", section_header_style))
    story.append(Paragraph("WHY THESE TALENTS WERE IDENTIFIED", h1_style))
    story.append(Paragraph("We cross-reference multiple independent psychometric indicators to establish evidence credibility. Below is the behavioral audit log for the top 2 domains:", body_style))
    story.append(Spacer(1, 5))
    
    for d_key in [x[0] for x in sorted_scores[:2]]:
        d_lbl = DOMAINS_MAP.get(d_key, d_key)
        d_color = DOMAIN_COLORS.get(d_key, primary_color)
        log = evidence.get(d_key, {})
        is_sufficient = log.get("has_preference") and log.get("has_behavioral") and log.get("has_performance")
        
        # Build evidence sub-table
        if is_sufficient:
            ev_table_data = [
                [
                    Paragraph("<b>👁️ Discovery Evidence</b>", card_label_style),
                    Paragraph("<b>🌱 Exposure Preference</b>", card_label_style),
                    Paragraph("<b>🎯 Performance Accuracy</b>", card_label_style)
                ],
                [
                    Paragraph(log.get("behavioral_desc", "N/A"), card_body_style),
                    Paragraph(log.get("preference_desc", "N/A"), card_body_style),
                    Paragraph(log.get("performance_desc", "N/A"), card_body_style)
                ]
            ]
            ev_table = Table(ev_table_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
            ev_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 6),
            ]))
        else:
            ev_table = Paragraph("<i>⚠️ Additional validation observations recommended. Prior exposure or behavioral inputs were insufficient for complete independent mapping.</i>", italic_style)
            
        domain_card = Table([[
            Paragraph(f"<font color='{d_color.hexval()}'><b>{d_lbl.upper()} INDICATORS</b></font>", styles['Heading4']),
        ], [
            ev_table
        ]], colWidths=[7.0 * inch])
        
        domain_card.setStyle(TableStyle([
            ('LINELEFT', (0,0), (0,-1), 4, d_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(domain_card)
        story.append(Spacer(1, 15))
        
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 5: HIDDEN OPPORTUNITIES (EXPOSURE VS POTENTIAL)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Hidden Opportunities", section_header_style))
    story.append(Paragraph("HIDDEN COGNITIVE OPPORTUNITIES", h1_style))
    story.append(Paragraph("This section highlights high-potential domains where the child demonstrated strong problem-solving capabilities despite very limited prior exposure or access. We define these as 'Untapped Potential'.", body_style))
    
    # Untapped potential display
    if untapped_potential:
        for u_key in untapped_potential:
            u_lbl = DOMAINS_MAP.get(u_key, u_key)
            u_score = integ.get(u_key, 0)
            exp_val = child.get(f"exp_{u_key}", 0)
            exp_lbl = ["Never tried it", "Tried a few times", "Sometimes", "Regularly"][exp_val]
            
            untapped_data = [
                [
                    Paragraph(f"<b>🔥 UNTAPPED POTENTIAL: {u_lbl.upper()}</b>", card_label_style),
                    Paragraph("<b>HIGH POTENTIAL &middot; LOW EXPOSURE</b>", ParagraphStyle('GoldBadge', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor("#B7791F"), alignment=2))
                ],
                [
                    Paragraph(f"{child.get('name', 'The student')} scored an impressive <b>{u_score}%</b> in cognitive puzzles for <b>{u_lbl}</b>, despite having very limited access opportunities in the past (Exposure Preference: '{exp_lbl}'). Actionable introductory workshops are highly recommended.", body_style),
                    ""
                ]
            ]
            untapped_table = Table(untapped_data, colWidths=[4.5 * inch, 2.5 * inch])
            untapped_table.setStyle(TableStyle([
                ('SPAN', (0,1), (1,1)),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFF9EE")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#F7B731")),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            story.append(untapped_table)
            story.append(Spacer(1, 15))
    else:
        empty_box = Table([[
            Paragraph("🌿 <b>No Untapped Potential Flags Detected</b><br/>All high-scoring cognitive domains align with positive prior exposure records. Keep supporting current nurturing tracks.", body_style)
        ]], colWidths=[7.0 * inch])
        empty_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#00B8A9")),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 14),
        ]))
        story.append(empty_box)
        story.append(Spacer(1, 20))
        
    story.append(Paragraph("DOMAIN POTENTIAL TIERS", h2_style))
    
    # Categorize domains by tier
    strong_list = [Paragraph(f"&bull; {DOMAINS_MAP[d]}", body_style) for d, s in sorted_scores if s >= 75]
    emerging_list = [Paragraph(f"&bull; {DOMAINS_MAP[d]}", body_style) for d, s in sorted_scores if 50 <= s < 75]
    explore_list = [Paragraph(f"&bull; {DOMAINS_MAP[d]}", body_style) for d, s in sorted_scores if s < 50]
    
    tiers_data = [
        [
            Paragraph("<b>Strong Potential (>=75%)</b>", card_label_style),
            Paragraph("<b>Emerging Potential (50-74%)</b>", card_label_style),
            Paragraph("<b>Further Observation (<50%)</b>", card_label_style)
        ],
        [
            strong_list or [Paragraph("None", body_style)],
            emerging_list or [Paragraph("None", body_style)],
            explore_list or [Paragraph("None", body_style)]
        ]
    ]
    tiers_table = Table(tiers_data, colWidths=[2.3 * inch, 2.3 * inch, 2.4 * inch])
    tiers_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEEDFE")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(tiers_table)
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 6: CHILD COGNITIVE PERSONA (CHILD ARCHETYPE)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Child Persona Profile", section_header_style))
    story.append(Paragraph("CHILD COGNITIVE PERSONA", h1_style))
    
    persona = PERSONAS.get(primary_domain, PERSONAS["creative"])
    
    # Archetype Card
    persona_card_data = [
        [Paragraph(f"<font size='44'>{persona['emoji']}</font>", styles['Normal'])],
        [Paragraph(f"<b>{persona['title']}</b>", ParagraphStyle('ArcTitle', parent=styles['Heading2'], textColor=primary_color, alignment=1, fontSize=16))],
        [Paragraph(persona['desc'], ParagraphStyle('ArcDesc', parent=body_style, alignment=1, fontSize=10, leading=15))]
    ]
    persona_card = Table(persona_card_data, colWidths=[7.0 * inch])
    persona_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EEECFF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#C3C0F9")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 20),
        ('RIGHTPADDING', (0,0), (-1,-1), 20),
    ]))
    story.append(persona_card)
    story.append(Spacer(1, 20))
    
    # Strengths / Growth Columns
    strengths_items = [Paragraph(f"&bull; <b>{s}</b>", body_style) for s in persona["strengths"]]
    growth_items = [Paragraph(f"&bull; <b>{g}</b>", body_style) for g in persona["growth"]]
    
    columns_data = [
        [
            Paragraph("<b>PRIMARY STRENGTHS</b>", card_label_style),
            "",
            Paragraph("<b>TARGETED GROWTH AREAS</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))
        ],
        [
            strengths_items,
            "",
            growth_items
        ]
    ]
    columns_table = Table(columns_data, colWidths=[3.4 * inch, 0.2 * inch, 3.4 * inch])
    columns_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#EEEDFE")),
        ('BACKGROUND', (2,0), (2,0), colors.HexColor("#E2F9F6")),
        ('BOX', (0,0), (0,-1), 0.5, border_color),
        ('BOX', (2,0), (2,-1), 0.5, border_color),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(columns_table)
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 7: PARENT & MENTOR GUIDE (LEARNING PROFILE)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Parent & Mentor Guide", section_header_style))
    story.append(Paragraph("UNDERSTANDING YOUR CHILD", h1_style))
    story.append(Paragraph(f"A tailored psychological roadmap to nurture {child.get('name', 'the student')}'s cognitive and educational preferences:", body_style))
    
    guide = parentGuides.get(primary_domain, parentGuides["creative"])
    
    # Behaviors Card
    b_items = [Paragraph(f"&bull; {b}", body_style) for b in guide["behaviors"]]
    c1 = Table([[Paragraph("<b>💡 Observed Learning Behaviors</b>", card_label_style)], [b_items]], colWidths=[7.0 * inch])
    c1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFFFF")),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c1)
    story.append(Spacer(1, 10))
    
    # Motivators Card
    c2 = Table([[
        Paragraph("<b>🎯 Motivators & Learning Styles</b>", card_label_style),
    ], [
        Paragraph(f"Learns best in a <b>{guide['styles']}</b> format, driven by <i>{guide['motivators']}</i>.", body_style)
    ]], colWidths=[7.0 * inch])
    c2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c2)
    story.append(Spacer(1, 10))
    
    # Challenges Card
    c3 = Table([[
        Paragraph("<b>⚠️ Potential Obstacles & Challenges</b>", ParagraphStyle('GoldLabel', parent=card_label_style, textColor=colors.HexColor("#B7791F"))),
    ], [
        Paragraph(f"{guide['challenges']}. May lose interest if forced into purely repetitive drills.", body_style)
    ]], colWidths=[7.0 * inch])
    c3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#F7B731")),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c3)
    story.append(Spacer(1, 10))
    
    # Support Card
    s_items = [Paragraph(f"&bull; {s}", body_style) for s in guide["support"]]
    c4 = Table([[Paragraph("<b>🛠️ Recommended Home Nurturing Support</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))], [s_items]], colWidths=[7.0 * inch])
    c4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#E2F9F6")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#00B8A9")),
        ('LEFTPADDING', (0,0), (-1,-1), 12), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(c4)
    
    story.append(PageBreak())
    
    # ──────────────────────────────────────────────────────────
    # PAGE 8: 30-DAY DEVELOPMENT ROADMAP (ACTION PLAN)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("30-Day Developmental Plan", section_header_style))
    story.append(Paragraph("DEVELOPMENT ROADMAP: NEXT STEPS", h1_style))
    story.append(Paragraph(f"A structured 4-week action roadmap to channelize cognitive indicators into active competencies:", body_style))
    
    # Grab week activities
    action_plan = analysis.get("action_plan") or {}
    w1 = action_plan.get("week_1") or f"Introductory hands-on exercises in the primary domain of {primary_label}."
    w2 = action_plan.get("week_2") or "Join collaborative center sessions and focus on shared peer group activities."
    w3 = action_plan.get("week_3") or f"Attempt open-ended puzzle/project challenge in {primary_label} without rigid templates."
    w4 = action_plan.get("week_4") or "Facilitator progress check-in, log milestones, and showcase child creations."
    
    roadmap_data = [
        [Paragraph("<b>Week 1: Activation</b>", body_style), Paragraph(w1, body_style)],
        [Paragraph("<b>Week 2: Collaboration</b>", body_style), Paragraph(w2, body_style)],
        [Paragraph("<b>Week 3: Challenge</b>", body_style), Paragraph(w3, body_style)],
        [Paragraph("<b>Week 4: Review</b>", body_style), Paragraph(w4, body_style)]
    ]
    roadmap_table = Table(roadmap_data, colWidths=[1.5 * inch, 5.5 * inch])
    roadmap_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,0), (0,-1), light_bg),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(roadmap_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Nurturing Guidelines", h2_style))
    story.append(Paragraph("<b>Home Action:</b> Share this roadmap with family. Schedule short, daily periods for focused solo play or creation. Acknowledge effort over outcomes.", body_style))
    story.append(Paragraph("<b>School Action:</b> Encourage the classroom teacher to assign leadership opportunities and group tasks that align with their cognitive strengths.", body_style))
    
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────
    # PAGE 9: DEVELOPMENT EXPLORATION PATHWAYS
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Exploration Pathways", section_header_style))
    story.append(Paragraph("TALENT PATHWAY SUGGESTIONS", h1_style))
    story.append(Paragraph(f"Based on {child.get('name', 'the student')}'s cognitive mapping, we recommend the following learning tracks:", body_style))
    story.append(Spacer(1, 10))
    
    # We look up top 2 domains from sorted_scores
    top_2_keys = [x[0] for x in sorted_scores[:2]]
    
    pathways_dict = {
        "creative": {
            "title": "Creative Arts & Visual Storytelling",
            "desc": "Visual expression, digital sketching, and storytelling workshops. Recommended: Project WHY Art Club, clay modelling, and design thinking modules."
        },
        "spatial": {
            "title": "Mechanical Design & 3D Prototyping",
            "desc": "Model building, LEGO engineering, origami, and basic architectural drafting. Recommended: Maker Space tinkering and hands-on physics toys."
        },
        "logical": {
            "title": "Math Olympiad & Coding Logic",
            "desc": "Scratch programming, chess, pattern recognition exercises, and basic algorithms. Recommended: Logic puzzles and computer science basics."
        },
        "social": {
            "title": "Community Leadership & Public Speaking",
            "desc": "Peer tutoring, student council, debate club, and team sports. Recommended: Team building workshops and local volunteering."
        },
        "language": {
            "title": "Creative Writing & Debate",
            "desc": "Story writing, speech competitions, spelling bees, and library reading clubs. Recommended: Theatre arts and presentation skills."
        },
        "naturalist": {
            "title": "Environmental Science & Eco-Clubs",
            "desc": "Plant care, bird watching, nature mapping, and ecology clubs. Recommended: Science lab experiments and gardening programs."
        },
        "kinesthetic": {
            "title": "Sports, Dance & Theatre",
            "desc": "Athletics, classical/modern dance, gymnastics, and physical theatre. Recommended: Martial arts and fine-motor craft work."
        },
        "intrapersonal": {
            "title": "Reflective Journalism & Goal Setting",
            "desc": "Diary writing, mindfulness, solo research projects, and goal tracking. Recommended: Self-paced online learning and reading programs."
        }
    }
    
    for i, key in enumerate(top_2_keys):
        path_info = pathways_dict.get(key, pathways_dict["creative"])
        p_color = DOMAIN_COLORS.get(key, primary_color)
        
        path_table_data = [
            [Paragraph(f"<b>RECOMMENDED TRACK {i+1}: {path_info['title'].upper()}</b>", card_label_style)],
            [Paragraph(path_info['desc'], body_style)]
        ]
        path_table = Table(path_table_data, colWidths=[7.0 * inch])
        path_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
            ('LINELEFT', (0,0), (0,-1), 4, p_color),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(path_table)
        story.append(Spacer(1, 15))
        
    story.append(Paragraph("<b>Pathway Engagement Tip:</b> Encourage child autonomy. Let them sample both tracks over the next 30 days and notice which one holds their focus longest without external rewards.", italic_style))
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────
    # PAGE 10: MENTOR REVIEW (FACILITATOR VALIDATION)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Mentor Validation & Review", section_header_style))
    story.append(Paragraph("FACILITATOR VALIDATION", h1_style))
    story.append(Paragraph("This page reflects direct observation notes from the classroom facilitator who conducted the cognitive assessment and monitored behavioral indicators.", body_style))
    
    # Progress Bar Drawing helper
    def draw_bar(rating, max_rating=5, width=120, height=8):
        d = Drawing(width, height)
        # Background bar
        d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#E2E8F0"), strokeColor=None))
        # Foreground filled bar
        fill_width = (rating / float(max_rating)) * width if rating else 0
        if fill_width > 0:
            d.add(Rect(0, 0, fill_width, height, fillColor=colors.HexColor("#00B8A9"), strokeColor=None))
        return d

    # Facilitator metrics table
    obs_metrics = [
        ("Creativity & Originality", note.get("obs_creativity", 3)),
        ("Communication & Clarity", note.get("obs_communication", 3)),
        ("Social Influence & Leadership", note.get("obs_leadership", 3)),
        ("Focused Engagement", note.get("obs_focus", 3)),
        ("Intellectual Curiosity", note.get("obs_curiosity", 3))
    ]
    
    metrics_table_data = [[
        Paragraph("<b>Observation Metric</b>", table_header_style),
        Paragraph("<b>Rating</b>", table_header_style),
        Paragraph("<b>Visual Level</b>", table_header_style)
    ]]
    
    for metric, rating in obs_metrics:
        try:
            rating_val = int(rating)
            if rating_val < 1: rating_val = 3
            if rating_val > 5: rating_val = 5
        except Exception:
            rating_val = 3
            
        bar_flowable = draw_bar(rating_val, max_rating=5, width=120, height=8)
        metrics_table_data.append([
            Paragraph(f"<b>{metric}</b>", table_cell_style),
            Paragraph(f"{rating_val} / 5", table_cell_style),
            bar_flowable
        ])
        
    m_table = Table(metrics_table_data, colWidths=[3.2 * inch, 1.2 * inch, 2.6 * inch])
    m_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
    ]))
    story.append(m_table)
    story.append(Spacer(1, 15))
    
    # Observations Log
    obs_text = note.get("observation") or "The student demonstrated positive focus and curiosity during the structured session."
    strengths_text = note.get("strengths_observed") or "Demonstrates rapid comprehension and willingness to attempt complex tasks."
    concerns_text = note.get("concerns") or "Requires occasional reassurance to handle open-ended tasks."
    rec_text = note.get("notes") or f"We suggest continuing to support {child.get('name', 'the student')} with creative arts or logical tasks."
    
    obs_box_data = [
        [Paragraph("<b>Facilitator Observations:</b>", card_label_style)],
        [Paragraph(obs_text, body_style)],
        [Paragraph("<b>Observed Strengths:</b>", card_label_style)],
        [Paragraph(strengths_text, body_style)],
        [Paragraph("<b>Areas for Support / Attention:</b>", ParagraphStyle('GoldLabel', parent=card_label_style, textColor=colors.HexColor("#B7791F")))],
        [Paragraph(concerns_text, body_style)],
        [Paragraph("<b>Validation Recommendations:</b>", ParagraphStyle('TealLabel', parent=card_label_style, textColor=secondary_color))],
        [Paragraph(rec_text, body_style)]
    ]
    obs_box = Table(obs_box_data, colWidths=[7.0 * inch])
    obs_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(obs_box)
    story.append(Spacer(1, 15))
    
    sig_data = [
        [Paragraph(f"<b>Facilitator Name:</b> {facilitator_name}", body_style), Paragraph(f"<b>Validation Date:</b> {formatted_date}", body_style)],
        [Paragraph("<b>Signature:</b> ___________________________", body_style), Paragraph("<b>Status:</b> Confirmed & Validated", body_style)]
    ]
    sig_table = Table(sig_data, colWidths=[3.5 * inch, 3.5 * inch])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(sig_table)
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────
    # PAGE 11: LONGITUDINAL GROWTH (GROWTH TIMELINE)
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Longitudinal Growth", section_header_style))
    story.append(Paragraph("DEVELOPMENT JOURNEY TIMELINE", h1_style))
    story.append(Paragraph("Tracking the student's primary cognitive domain shifts and score stability across successive assessment sessions. This ensures our talent identification remains dynamic rather than static.", body_style))
    
    if len(history) > 1:
        hist_table_data = [[
            Paragraph("<b>Assessment Date</b>", table_header_style),
            Paragraph("<b>Session ID</b>", table_header_style),
            Paragraph("<b>Top Domain Mapped</b>", table_header_style),
            Paragraph("<b>Milestone Description</b>", table_header_style)
        ]]
        for idx, hist_row in enumerate(history):
            h_date_val = hist_row["completed_at"] or hist_row["created_at"]
            try:
                if isinstance(h_date_val, str):
                    if "." in h_date_val: h_date_val = h_date_val.split(".")[0]
                    if "T" in h_date_val:
                        h_dt = datetime.strptime(h_date_val, "%Y-%m-%dT%H:%M:%S")
                    else:
                        h_dt = datetime.strptime(h_date_val, "%Y-%m-%d %H:%M:%S")
                else:
                    h_dt = h_date_val
                h_date_str = h_dt.strftime("%d %b %Y")
            except Exception:
                h_date_str = str(h_date_val)[:10]
                
            h_top = DOMAINS_MAP.get(hist_row["top_domain"], hist_row["top_domain"] or "N/A")
            h_sid = f"GOAT-SESS-{hist_row['id']}"
            
            if idx == 0:
                m_desc = "Baseline preferences mapped."
            elif idx == 1:
                m_desc = "Talent stabilization & growth verified."
            else:
                m_desc = "Longitudinal talent track active."
                
            hist_table_data.append([
                Paragraph(h_date_str, table_cell_style),
                Paragraph(h_sid, table_cell_style),
                Paragraph(h_top, table_cell_style),
                Paragraph(m_desc, table_cell_style)
            ])
            
        hist_table = Table(hist_table_data, colWidths=[1.5 * inch, 1.5 * inch, 2.0 * inch, 2.0 * inch])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_bg]),
        ]))
        story.append(hist_table)
    else:
        baseline_data = [
            [
                Paragraph("<b>Milestone 1 (Current Session)</b>", card_label_style),
                Paragraph(f"Baseline preferences established. Primary Talent Domain identified as <b>{primary_label}</b>.", body_style)
            ],
            [
                Paragraph("<b>Milestone 2 (Month 6 Target)</b>", card_label_style),
                Paragraph("Scheduled check-in to trace preference migration, domain stabilization, and child development milestones.", body_style)
            ],
            [
                Paragraph("<b>Milestone 3 (Month 12 Target)</b>", card_label_style),
                Paragraph("Advanced skill mapping, assessing performance stability and hands-on portfolio review.", body_style)
            ]
        ]
        baseline_table = Table(baseline_data, colWidths=[2.2 * inch, 4.8 * inch])
        baseline_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), light_bg),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(baseline_table)
        story.append(Spacer(1, 15))
        story.append(Paragraph("<b>Note:</b> We recommend a follow-up assessment every 6 months to maintain an active, accurate developmental track as the child matures.", italic_style))
        
    story.append(PageBreak())

    # ──────────────────────────────────────────────────────────
    # PAGE 12: METHODOLOGY & DISCLOSURE
    # ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 15))
    story.append(Paragraph("Methodology & Disclosure", section_header_style))
    story.append(Paragraph("ASSESSMENT METHODOLOGY", h1_style))
    
    methodology_text = (
        "The GOAT Talent Mapping framework integrates multiple data points to evaluate "
        "a student's developmental indicators. The framework consists of four primary stages:<br/>"
        "1. <b>Cognitive Puzzles</b>: Abstract, language-neutral puzzles to measure pattern recognition and reasoning.<br/>"
        "2. <b>Prior Exposure Logs</b>: Mappings of historical familiarity to distinguish natural preference from taught capability.<br/>"
        "3. <b>Facilitator Observation</b>: Structured classroom observations to capture behavioral indicators (focus, leadership, communication).<br/>"
        "4. <b>Integration Engine</b>: Normalization algorithms that synthesize these signals into a structured profile."
    )
    story.append(Paragraph(methodology_text, body_style))
    story.append(Spacer(1, 20))
    
    disc_data = [[
        Paragraph("<b>⚠️ DEVELOPMENTAL AND ASSESSMENT DISCLOSURE</b>", ParagraphStyle('GoldHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#B7791F"))),
    ], [
        Paragraph(
            "This Talent Discovery & Development Report is designed purely as an educational advisory document. "
            "It is NOT a standardized IQ test, nor does it measure fixed academic potential. "
            "Cognitive preferences and interests in childhood are highly plastic and evolve continuously with exposure, encouragement, and emotional safety. "
            "We strongly caution against using these results to label the child, restrict their educational pathways, or enforce a rigid specialization. "
            "Instead, please use this report as an invitation to offer diverse exposures, support emerging strengths, and nurture growth areas with patience.",
            body_style
        )
    ]]
    disc_table = Table(disc_data, colWidths=[7.0 * inch])
    disc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFDF0")),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#F7B731")),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
    ]))
    story.append(disc_table)

    # ──────────────────────────────────────────────────────────
    # BACKGROUND CALLBACKS FOR PAGE 1 (COVER) AND PAGE NUMBERS
    # ──────────────────────────────────────────────────────────
    def draw_cover_page(canvas, doc):
        canvas.saveState()
        # Left indigo stripe background
        canvas.setFillColor(colors.HexColor("#5B4CF0"))
        canvas.rect(0, 0, 160, 792, fill=1, stroke=0)
        
        # Gold accent stripe
        canvas.setFillColor(colors.HexColor("#F7B731"))
        canvas.rect(160, 0, 5, 792, fill=1, stroke=0)
        
        # Concentric faint white decorative arcs
        canvas.setStrokeColor(colors.HexColor("#7C6FFE"))
        canvas.setLineWidth(1)
        canvas.circle(0, 396, 100, fill=0, stroke=1)
        canvas.circle(0, 396, 140, fill=0, stroke=1)
        canvas.circle(0, 396, 180, fill=0, stroke=1)
        
        # Project WHY Logo
        why_logo_path = os.path.join(os.path.dirname(__file__), "why_logo.jpg")
        if os.path.exists(why_logo_path):
            canvas.drawImage(why_logo_path, 185, 685, width=30, height=30, mask='auto')
        else:
            canvas.setFillColor(colors.HexColor("#00B8A9"))
            canvas.circle(200, 700, 15, fill=1, stroke=0)
            canvas.setStrokeColor(colors.white)
            canvas.setLineWidth(2.5)
            canvas.line(200, 700, 200, 690)
            canvas.line(200, 700, 192, 708)
            canvas.line(200, 700, 208, 708)
        
        canvas.setFillColor(colors.HexColor("#2D3436"))
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(225, 696, "PROJECT WHY")
        
        # GOAT Logo next to it
        goat_logo_path = os.path.join(os.path.dirname(__file__), "goat_logo.png")
        if os.path.exists(goat_logo_path):
            canvas.drawImage(goat_logo_path, 360, 685, width=30, height=30, mask='auto')
        else:
            canvas.setFillColor(colors.HexColor("#5B4CF0"))
            canvas.rect(360, 685, 30, 30, fill=1, stroke=0)
            canvas.setStrokeColor(colors.white)
            canvas.setLineWidth(3.0)
            canvas.line(375, 690, 375, 710)
            canvas.line(367, 710, 383, 710)
        
        canvas.setFillColor(colors.HexColor("#2D3436"))
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(400, 696, "GOAT TALENT LAB")
        
        # Report Title
        canvas.setFillColor(colors.HexColor("#5B4CF0"))
        canvas.setFont("Helvetica-Bold", 24)
        canvas.drawString(200, 520, "Talent Discovery &")
        canvas.drawString(200, 485, "Development Report")
        
        # Tagline
        canvas.setFillColor(colors.HexColor("#2D3436"))
        canvas.setFont("Helvetica-Oblique", 11)
        canvas.drawString(200, 455, "Understanding Potential. Building Futures.")
        
        # Thin gold divider line
        canvas.setStrokeColor(colors.HexColor("#F7B731"))
        canvas.setLineWidth(1.5)
        canvas.line(200, 435, 520, 435)
        
        # Metadata
        metadata = [
            ("STUDENT NAME", child.get("name", "N/A").upper()),
            ("AGE", f"{child.get('age', 'N/A')} YEARS"),
            ("CLASS / LEVEL", (child.get("school_year") or "N/A").upper()),
            ("ASSESSMENT DATE", formatted_date.upper()),
            ("ASSESSMENT ID", f"GOAT-SESS-{sid}"),
            ("FACILITATOR", facilitator_name.upper())
        ]
        
        y_pos = 380
        for label, val in metadata:
            canvas.setFillColor(colors.HexColor("#94A3B8"))
            canvas.setFont("Helvetica-Bold", 8.5)
            canvas.drawString(200, y_pos, label)
            
            canvas.setFillColor(colors.HexColor("#2D3436"))
            canvas.setFont("Helvetica-Bold", 10.5)
            canvas.drawString(200, y_pos - 15, val)
            
            y_pos -= 40
            
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.setFont("Helvetica-Bold", 8.0)
        canvas.drawRightString(letter[0]-54, 40, "CONFIDENTIAL & PROPRIETARY")
        canvas.restoreState()

    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8.5)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        
        if doc.page > 1:
            canvas.drawString(54, 750, "GOAT TALENT IDENTIFICATION SYSTEM REPORT")
            canvas.drawRightString(letter[0]-54, 750, "PROJECT WHY / GOAT")
            canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
            canvas.setLineWidth(0.5)
            canvas.line(54, 742, letter[0]-54, 742)
            
            page_num = canvas.getPageNumber()
            canvas.drawString(54, 36, "CONFIDENTIAL DEVELOPMENTAL REPORT")
            canvas.drawRightString(letter[0]-54, 36, f"Page {page_num} of 12")
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_cover_page, onLaterPages=add_page_number)
    
    pdf_buffer.seek(0)
    return Response(
        pdf_buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-disposition": f"attachment; filename={child['name'].replace(' ', '_')}_GOAT_Talent_Report.pdf"}
    )



# Initialize database on import (Gunicorn/production compatibility)
init_db()

if __name__ == "__main__":
    print("\n[SUCCESS] GOAT backend running at http://localhost:5050\n")
    app.run(port=5050, debug=True, use_reloader=False)
