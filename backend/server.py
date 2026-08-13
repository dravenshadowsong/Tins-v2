"""
GOAT Backend — Flask + SQLite
Greatest of All Talents System
"""
import os
import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
import threading
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

# ── In-memory JWT token cache (avoids calling supabase.auth.get_user on every request) ──
_token_cache = {}  # token -> {user_dict, expires_at}
_token_cache_lock = threading.Lock()
TOKEN_CACHE_TTL_SECONDS = 300  # 5 minutes

def _get_cached_user(token):
    with _token_cache_lock:
        entry = _token_cache.get(token)
        if entry and datetime.utcnow() < entry["expires_at"]:
            return entry["user"]
        elif entry:
            del _token_cache[token]
    return None

def _set_cached_user(token, user_dict):
    with _token_cache_lock:
        _token_cache[token] = {
            "user": user_dict,
            "expires_at": datetime.utcnow() + timedelta(seconds=TOKEN_CACHE_TTL_SECONDS)
        }
        # Evict expired entries to prevent memory growth
        now = datetime.utcnow()
        expired = [k for k, v in _token_cache.items() if now >= v["expires_at"]]
        for k in expired:
            del _token_cache[k]

def _invalidate_token_cache(token):
    with _token_cache_lock:
        _token_cache.pop(token, None)

def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    token = auth.replace("Bearer ", "", 1).strip()
    if not token:
        return None

    # Check if this is a Supabase JWT token
    if token.startswith("eyJ") and supabase:
        # Fast path: return cached user if still valid (avoids Supabase network round-trip)
        cached = _get_cached_user(token)
        if cached:
            return cached

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
                    user_dict = dict(row)
                    _set_cached_user(token, user_dict)
                    return user_dict
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
                        user_dict = dict(row)
                        _set_cached_user(token, user_dict)
                        return user_dict
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
            
            # Migration check: Add exposure_data if not exists
            try:
                cursor.execute("ALTER TABLE children ADD COLUMN IF NOT EXISTS exposure_data TEXT")
                conn.commit()
            except Exception as e_alter:
                print(f"[DATABASE WARNING] Failed to dynamically alter children on Postgres: {e_alter}")
                conn.rollback()

            # Migration check: Add timing_data to sessions if not exists
            try:
                cursor.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS timing_data TEXT")
                conn.commit()
            except Exception as e_alter:
                print(f"[DATABASE WARNING] Failed to add timing_data to sessions on Postgres: {e_alter}")
                conn.rollback()
                
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
            timing_data     TEXT,
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
                "center_id": "INTEGER REFERENCES centers(id) ON DELETE SET NULL",
                "exposure_data": "TEXT"
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
                "timing_data": "TEXT",
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
        # Invalidate cached token entry so revoked tokens are not served from cache
        _invalidate_token_cache(token)
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
        if d.get("exposure_data"):
            try:
                d["exposure_data"] = json.loads(d["exposure_data"])
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

    exposure_val = json.dumps(data.get("exposure_data")) if data.get("exposure_data") else None

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
                "center_id": center_id,
                "exposure_data": exposure_val
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
                   organization_id, center_id, exposure_data)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                supabase_id,
                data["name"], data["age"], data.get("language", "Hindi"),
                data.get("school_year", ""), data.get("gender", ""),
                data.get("exp_kinesthetic", 0), data.get("exp_creative", 0),
                data.get("exp_logical", 0),    data.get("exp_spatial", 0),
                data.get("exp_social", 0),     data.get("exp_language", 0),
                data.get("exp_naturalist", 0), data.get("exp_intrapersonal", 0),
                org_id, center_id,
                exposure_val
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
               organization_id, center_id, exposure_data)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["name"], data["age"], data.get("language", "Hindi"),
            data.get("school_year", ""), data.get("gender", ""),
            data.get("exp_kinesthetic", 0), data.get("exp_creative", 0),
            data.get("exp_logical", 0),    data.get("exp_spatial", 0),
            data.get("exp_social", 0),     data.get("exp_language", 0),
            data.get("exp_naturalist", 0), data.get("exp_intrapersonal", 0),
            org_id, center_id,
            exposure_val
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
    if child_dict.get("exposure_data"):
        try:
            child_dict["exposure_data"] = json.loads(child_dict["exposure_data"])
        except Exception:
            pass

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
def _load_default_puzzles():
    try:
        path = os.path.join(os.path.dirname(__file__), "db", "question_bank", "extended_bank.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[DATABASE WARNING] Failed to load default puzzles from json: {e}")
    return []

DEFAULT_AI_PUZZLES = _load_default_puzzles()
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
        "title": {"English": "Odd One Out", "Hindi": "अलग कौन?"},
        "prompt": {
            "English": "Cow, horse, dog, crow — which one is different from the others? 🐦",
            "Hindi": "गाय, घोड़ा, कुत्ता, कौवा — इनमें से कौन सा अलग है? 🐦"
        }
    },
    "spatial_rotation": {
        "title": {"English": "Spinning Arrow", "Hindi": "घूमता तीर"},
        "prompt": {
            "English": "An arrow on paper points UP. You flip the paper over (like flipping a chapati). Which way does the arrow point now? ↓",
            "Hindi": "कागज पर एक तीर ऊपर की ओर इशारा कर रहा है। आप कागज को पलट देते हैं (चपाती की तरह)। अब तीर किधर इशारा करेगा? ↓"
        }
    },
    "spatial_perspective": {
        "title": {"English": "Shadow Match", "Hindi": "परछाई का खेल"},
        "prompt": {
            "English": "A T-shaped toy has light shining from the LEFT. What shape of shadow does it make on the wall?",
            "Hindi": "एक 'T' आकार के खिलौने पर बाईं (LEFT) ओर से टॉर्च की रोशनी पड़ने पर दीवार पर कैसी छाया बनेगी?"
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
    db_puzzles = load_puzzles_from_db()
    
    # 1. Filter and sort Core Deep questions (exactly 2 per domain)
    core_deep = [p for p in db_puzzles if p.get("component") == "core_deep"]
    domain_order = ["logical", "spatial", "creative", "language", "kinesthetic", "social", "naturalist", "intrapersonal"]
    core_deep_sorted = sorted(
        core_deep, 
        key=lambda x: domain_order.index(x["domain"]) if x["domain"] in domain_order else 9
    )
    
    # 2. Filter Reflection questions (exactly 4)
    reflection = [p for p in db_puzzles if p.get("component") == "reflection"]
    # Sort reflection questions by key to keep a stable order
    reflection_sorted = sorted(reflection, key=lambda x: x.get("key", ""))
    
    return core_deep_sorted + reflection_sorted



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

@app.route("/api/sessions/<int:sid>/adaptive", methods=["POST"])
def get_adaptive_questions_route(sid):
    data = request.json or {}
    responses = data.get("responses", {})
    child_id = data.get("child_id")
    
    db = get_db()
    child = db.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not child:
        return jsonify({"error": "Child not found"}), 404
    child = dict(child)
    
    # Load discovery answers
    session_row = db.execute("SELECT responses, generated_tasks FROM sessions WHERE id=?", (sid,)).fetchone()
    if not session_row:
        return jsonify({"error": "Session not found"}), 404
        
    discovery_answers = {}
    if session_row["responses"]:
        try:
            discovery_answers = json.loads(session_row["responses"])
        except Exception:
            pass
            
    # Calculate preliminary scores to identify Primary, Secondary, Emerging domains
    scores = score_responses(responses, child, discovery_answers)
    
    primary = scores["primary_domain"]
    secondary = scores["secondary_domains"][0] if scores["secondary_domains"] else "creative"
    
    # Select emerging domain: first one from emerging_domains list or fallback
    emerging = scores["emerging_domains"][0] if scores["emerging_domains"] else "spatial"
    
    # Load all puzzles from the DB
    all_puzzles = load_puzzles_from_db()
    
    # Filter for adaptive puzzles
    adaptive_bank = [p for p in all_puzzles if p.get("component") == "adaptive"]
    
    # If bank is empty, fall back to default adaptive questions
    selected_adaptive = []
    for dom in [primary, secondary, emerging]:
        dom_puzzles = [p for p in adaptive_bank if p["domain"] == dom]
        # Sort or take first 2
        selected_adaptive.extend(dom_puzzles[:2])

    # Fix: Always guarantee at least 1 adaptive kinesthetic question is served.
    # Without this, if kinesthetic didn't emerge as top-3 after discovery it would
    # receive zero adaptive weight (15% of blended score silently absent), making
    # it almost impossible for physical-learners to surface as a top domain.
    selected_keys = {p["key"] for p in selected_adaptive}
    kinesthetic_adaptive = [p for p in adaptive_bank if p["domain"] == "kinesthetic" and p["key"] not in selected_keys]
    if kinesthetic_adaptive:
        selected_adaptive.append(kinesthetic_adaptive[0])
        
    # Append to existing generated tasks in the session
    existing_tasks = []
    if session_row["generated_tasks"]:
        try:
            existing_tasks = json.loads(session_row["generated_tasks"])
        except Exception:
            pass
            
    # Remove any existing adaptive questions to prevent duplicates on refresh
    existing_tasks = [t for t in existing_tasks if t.get("component") != "adaptive" and not t["key"].startswith("adaptive_")]
    
    new_tasks = existing_tasks + selected_adaptive
    
    # Update SQLite session
    db.execute("""
        UPDATE sessions SET generated_tasks = ? WHERE id = ?
    """, (json.dumps(new_tasks), sid))
    db.commit()
    
    # Update Supabase Postgres session if available
    if supabase_client:
        try:
            supabase_client.table("sessions").update({
                "generated_tasks": json.dumps(new_tasks)
            }).eq("id", sid).execute()
        except Exception as e:
            print(f"DEBUG: Exception updating adaptive tasks in Supabase: {e}")
            
    return jsonify({
        "status": "success",
        "primary": primary,
        "secondary": secondary,
        "emerging": emerging,
        "adaptive_tasks": selected_adaptive
    })

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

@app.route("/api/sessions/<int:sid>/timing", methods=["POST"])
@app.route("/api/sessions/<int:sid>/timing/", methods=["POST"])
def save_session_timing(sid):
    """
    Saves assessment timing data (session-level + question-level) for research,
    psychometric analytics, and future AI improvements.

    This endpoint NEVER modifies scoring, AI analysis, or report data.
    It is purely additive and always returns 200 so that a client failure
    never blocks the assessment flow.

    Expected payload (all optional for forward-compatibility):
    {
      "session_start_iso": "...",
      "session_end_iso":   "...",
      "total_seconds":     1236,
      "total_formatted":   "00:20:36",
      "question_timings":  [...],
      "analytics":         {...}
    }
    """
    try:
        data = request.json or {}
        if not data:
            return jsonify({"status": "skipped", "reason": "empty payload"}), 200

        db = get_db()
        # Verify session exists
        row = db.execute("SELECT id FROM sessions WHERE id=?", (sid,)).fetchone()
        if not row:
            return jsonify({"status": "skipped", "reason": "session not found"}), 200

        timing_json = json.dumps(data)

        # Save to local DB
        try:
            db.execute(
                "UPDATE sessions SET timing_data = ? WHERE id = ?",
                (timing_json, sid)
            )
            db.commit()
        except Exception as e:
            print(f"[TIMING] SQLite save failed for session {sid}: {e}")

        # Save to Supabase if available
        if supabase_client:
            try:
                supabase_client.table("sessions").update(
                    {"timing_data": timing_json}
                ).eq("id", sid).execute()
            except Exception as e:
                print(f"[TIMING] Supabase save failed for session {sid}: {e}")

        return jsonify({"status": "saved"}), 200

    except Exception as e:
        # Graceful failure — never block the client
        print(f"[TIMING] Unexpected error for session {sid}: {e}")
        return jsonify({"status": "error", "reason": str(e)}), 200

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
    responses = dict(data.get("responses", {}))
    # Extract optional timing payload (never required; does not affect scoring)
    timing_payload = data.get("timing")
    # Ensure both V5 and V4 keys are present in responses for backward/forward compatibility
    key_mapping = {
        "reflection_flow": "deep_discovery_flow",
        "reflection_pride": "deep_discovery_pride",
        "reflection_learning": "deep_discovery_curiosity",
        "reflection_community": "deep_discovery_vision"
    }
    for new_k, old_k in key_mapping.items():
        if new_k in responses and old_k not in responses:
            responses[old_k] = responses[new_k]
        elif old_k in responses and new_k not in responses:
            responses[new_k] = responses[old_k]
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
            # Save timing data if provided by the frontend (never required)
            if timing_payload:
                try:
                    update_data["timing_data"] = json.dumps(timing_payload)
                except Exception:
                    pass
            print(f"DEBUG: Attempting Supabase update for session ID: {sid}")
            # print(f"DEBUG: Supabase update payload: {json.dumps(update_data)}")
            res = supabase_client.table("sessions").update(update_data).eq("id", sid).execute()
            # print(f"DEBUG: Supabase update response data: {res.data}")
        except Exception as e:
            print(f"DEBUG: EXCEPTION caught during Supabase update: {str(e)[:200]}")

    # Build the timing data value (None if not provided)
    timing_data_value = None
    if timing_payload:
        try:
            timing_data_value = json.dumps(timing_payload)
        except Exception:
            pass

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
            timing_data      = ?,
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
        timing_data_value,
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
    "kinesthetic":   {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "creative":      {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "logical":       {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "spatial":       {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "social":        {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "language":      {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "naturalist":    {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
    "intrapersonal": {"performance_1":25, "performance_2":25, "situational":25, "open_response":25},
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

    obs_ratings = {
        "curiosity": int(data.get("obs_curiosity", 3)),
        "confidence": int(data.get("obs_confidence", 3)),
        "focus": int(data.get("obs_focus", 3)),
        "creativity": int(data.get("obs_creativity", 3)),
        "communication": int(data.get("obs_communication", 3)),
        "leadership": int(data.get("obs_leadership", 3)),
        "persistence": int(data.get("obs_persistence", 3)),
        "emotional_regulation": int(data.get("obs_emotional_regulation", 3))
    }
    observation_text = json.dumps(obs_ratings)

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
        observation_text, data.get("override_domain", ""),
        data.get("notes", ""),
        data.get("agreement", "Agree"),
        data.get("strengths_observed", ""),
        data.get("concerns", ""),
        data.get("suggested_workshop", ""),
        int(data.get("obs_creativity", 3)),
        int(data.get("obs_communication", 3)),
        int(data.get("obs_leadership", 3)),
        int(data.get("obs_focus", 3)),
        data.get("evidence_notes", ""),
        int(data.get("obs_curiosity", 3)),
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

    # For open-ended text answers, score them based on word count (0 to 4 scale)
    if answer.get("task_type") == "open_ended" or answer.get("component") == "open_response":
        text = answer.get("value", "") or answer.get("text", "") or ""
        if not isinstance(text, str):
            text = str(text)
        words = len(text.strip().split())
        if words >= 15:
            return 4.0
        elif words >= 5:
            return 2.4
        elif words >= 1:
            return 1.2
        return 0.0

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
    exposure_data = child.get("exposure_data")
    if isinstance(exposure_data, str) and exposure_data:
        try:
            exposure_data = json.loads(exposure_data)
        except Exception:
            exposure_data = None
            
    if exposure_data and isinstance(exposure_data, dict):
        q = {}
        for i in range(1, 13):
            q[f"q{i}"] = float(exposure_data.get(f"q{i}", 0))
            
        domain_exposures = {
            "logical": (q["q1"] + q["q2"]) / 2.0,
            "spatial": (q["q3"] + q["q1"]) / 2.0,
            "creative": (q["q4"] + q["q5"]) / 2.0,
            "kinesthetic": (q["q8"] + q["q5"]) / 2.0,
            "language": (q["q11"] + q["q6"]) / 2.0,
            "social": (q["q7"] + q["q6"]) / 2.0,
            "naturalist": q["q9"],
            "intrapersonal": (q["q11"] + q["q12"]) / 2.0
        }
        exposure_scores = {dom: int(round((val / 4.0) * 100)) for dom, val in domain_exposures.items()}
    else:
        exposure_scores = {}
        for domain in final_scores.keys():
            exp_val = child.get(f"exp_{domain}", 0)
            exposure_scores[domain] = int(round((exp_val / 3.0) * 100))

    teg_data = {}
    for domain, talent_score in final_scores.items():
        exposure_score = exposure_scores.get(domain, 0)
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
    Core scoring engine for V5.
    Blends:
    - 20% Discovery / Spontaneous Preference
    - 50% Core Deep Assessment / Demonstrated Ability
    - 15% Reflection
    - 15% Adaptive Assessment
    - 0% Exposure (Opportunity/TEG only)
    """
    responses = dict(responses)
    # Ensure both V5 and V4 keys are present in responses for backward/forward compatibility
    key_mapping = {
        "reflection_flow": "deep_discovery_flow",
        "reflection_pride": "deep_discovery_pride",
        "reflection_learning": "deep_discovery_curiosity",
        "reflection_community": "deep_discovery_vision"
    }
    for new_k, old_k in key_mapping.items():
        if new_k in responses and old_k not in responses:
            responses[old_k] = responses[new_k]
        elif old_k in responses and new_k not in responses:
            responses[new_k] = responses[old_k]

    
    # V5 Discovery Mapping
    discovery_mapping = {
        "q_discovery_1": {0: ["language", "creative"], 1: ["logical", "spatial"], 2: ["social", "language"], 3: ["intrapersonal"]},
        "q_discovery_2": {0: ["creative", "spatial"], 1: ["spatial", "logical"], 2: ["social", "language"], 3: ["intrapersonal"]},
        "q_discovery_3": {0: ["logical", "spatial"], 1: ["creative", "spatial"], 2: ["language", "social"], 3: ["intrapersonal"]},
        "q_discovery_4": {0: ["spatial", "logical"], 1: ["kinesthetic", "spatial"], 2: ["social", "language"], 3: ["intrapersonal"]},
        "q_discovery_5": {0: ["kinesthetic", "creative"], 1: ["logical", "naturalist"], 2: ["social", "language"], 3: ["intrapersonal"]},
        "q_discovery_6": {0: ["naturalist", "logical"], 1: ["creative", "naturalist"], 2: ["language", "social"], 3: ["intrapersonal"]},
        "q_discovery_7": {0: ["language", "social"], 1: ["kinesthetic", "social"], 2: ["intrapersonal"], 3: ["creative", "social"]},
        "q_discovery_8": {0: ["intrapersonal", "logical"], 1: ["creative"], 2: ["social", "language"], 3: ["kinesthetic"]},
        # Two new questions that give kinesthetic a solo-signal channel
        "q_discovery_9": {0: ["kinesthetic"], 1: ["logical", "spatial"], 2: ["creative"], 3: ["intrapersonal"]},
        "q_discovery_10": {0: ["social", "language"], 1: ["kinesthetic"], 2: ["naturalist"], 3: ["intrapersonal"]}
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
                        doms = opts[choice_val]
                        for dom in doms:
                            discovery_counts[dom] += 1
                except Exception:
                    pass

    # Form mapping for evidence log
    FORMAL_MAPPING = {
        "logical_lock": "Pattern Completion",
        "logical_legs": "Visual Reasoning",
        "spatial_shape_match": "Puzzle Piece Selection",
        "spatial_clock": "Shape Rotation",
        "creative_circles": "Circle Transformation",
        "creative_box_situational": "Cardboard Box Creation",
        "language_race": "Story Sequencing",
        "language_explain_game": "Explaining to Younger Child",
        "visualizer_memory_grid": "Memory Sequence Grid",
        "kinesthetic_catch": "Action Pattern Recognition",
        "naturalist_weather": "Nature Observation",
        "naturalist_plants": "Plant Difference Spotting",
        "social_planning": "Team Task Delegation",
        "social_conflict_resolution": "Playground Mediator",
        "intrapersonal_goals": "Goal Setting Practice",
        "intrapersonal_reflection": "Growth Mindset Challenge",
        
        "adaptive_language_story": "Story Interpretation",
        "adaptive_language_teach": "Teaching Challenge",
        "adaptive_creative_transform": "Object Transformation",
        "adaptive_creative_design": "Symbolic Design",
        "adaptive_logical_reasoning": "Multi-Step Deduction",
        "adaptive_logical_problem": "Resource Allocation",
        "adaptive_spatial_construction": "Structural Stability",
        "adaptive_spatial_reasoning": "Spatial Net Folding",
        "adaptive_kinesthetic_strategy": "Movement Strategy",
        "adaptive_kinesthetic_learning": "Skill Breakdown",
        "adaptive_naturalist_observation": "Ecosystem Diagnosis",
        "adaptive_naturalist_problem": "Water Scarcity Solution",
        "adaptive_social_conflict": "Group Dispute Resolution",
        "adaptive_social_planning": "Community Task Organization",
        "adaptive_intrapersonal_reflection": "Competition Resilience",
        "adaptive_intrapersonal_goals": "Goal Planning & Tracking"
    }

    evidence = {}
    for domain in DOMAIN_WEIGHTS.keys():
        exp_val = child.get(f"exp_{domain}", 0) or 0
        has_pref = exp_val >= 1
        pref_label = ["Never tried it", "Tried a few times", "Do it sometimes", "Do it regularly"][exp_val]
        pref_desc = f"Observed exposure preference: '{pref_label}'" if has_pref else "No prior preference or regular exposure observed."

        disc_count = discovery_counts.get(domain, 0)
        has_behav = disc_count >= 1
        behav_desc = f"Selected spontaneous behavior in {disc_count} discovery scenarios" if has_behav else "No spontaneous behavior observed in discovery scenarios."

        perf_tasks = []
        for q_key, answer in responses.items():
            if isinstance(answer, dict) and answer.get("domain") == domain:
                score = answer_to_scale(answer)
                if score >= 2.0:
                    perf_tasks.append(q_key)
        has_perf = len(perf_tasks) >= 1
        
        task_categories = list(set([FORMAL_MAPPING.get(t, t.replace("_", " ").title()) for t in perf_tasks]))
        perf_desc = f"Demonstrated accuracy in {len(perf_tasks)} puzzles: {', '.join(task_categories[:2])}" if has_perf else "Performance on scored cognitive challenges was insufficient to establish independent evidence."

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

    blended = {}
    for domain in DOMAIN_WEIGHTS.keys():
        # 1. Discovery (20%)
        s_disc = min(100.0, (discovery_counts.get(domain, 0) / 3.0) * 100.0)
        
        # 2. Core Deep (50%) & Adaptive (15%)
        core_deep_scores = []
        adaptive_scores = []
        for q_key, answer in responses.items():
            if not isinstance(answer, dict):
                continue
            if answer.get("domain") != domain:
                continue
            comp = answer.get("component", "")
            if comp == "adaptive" or q_key.startswith("adaptive_"):
                adaptive_scores.append(answer_to_scale(answer))
            else:
                core_deep_scores.append(answer_to_scale(answer))
                
        s_deep = (sum(core_deep_scores) / (len(core_deep_scores) * 4.0)) * 100.0 if core_deep_scores else 50.0
        
        # 3. Reflection (15%)
        s_pride = get_text_completion_score(responses.get("reflection_pride"))
        s_flow = get_text_completion_score(responses.get("reflection_flow"))
        s_learning = get_text_completion_score(responses.get("reflection_learning"))
        s_community = get_text_completion_score(responses.get("reflection_community"))
        if domain == "intrapersonal":
            s_refl = (s_pride + s_flow + s_learning) / 3.0
        elif domain == "social":
            s_refl = s_community
        else:
            s_refl = (s_pride + s_flow + s_learning + s_community) / 4.0
            
        # 4. Adaptive Assessment (15%)
        if adaptive_scores:
            s_adap = (sum(adaptive_scores) / (len(adaptive_scores) * 4.0)) * 100.0
            blended[domain] = 0.20 * s_disc + 0.50 * s_deep + 0.15 * s_refl + 0.15 * s_adap
        else:
            # No adaptive questions answered for this domain, scale weights of remaining parts (85% total) to 100%
            raw_unscaled = 0.20 * s_disc + 0.50 * s_deep + 0.15 * s_refl
            blended[domain] = (raw_unscaled / 0.85)

    tq_raw_scores = {}
    for domain in DOMAIN_WEIGHTS.keys():
        all_deep = []
        for q_key, answer in responses.items():
            if isinstance(answer, dict) and answer.get("domain") == domain:
                all_deep.append(answer_to_scale(answer))
        tq_raw_scores[domain] = (sum(all_deep) / (len(all_deep) * 4.0)) * 100.0 if all_deep else 50.0

    # Calculate original top domain before overrides or validation adjustments
    original_top = max(blended.items(), key=lambda x: x[1])[0] if blended else "unknown"

    # Handle facilitator overrides if confirmed/override_domain is set
    # Maintain standard TM profile logic but do NOT alter finalstretched/GTI score with notes.
    # We will compute the final blended scores.
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

    # If facilitator override is provided, we can blend it to adjust top list
    blended_final = {}
    for domain in DOMAIN_WEIGHTS.keys():
        if has_notes and facilitator_note.get("override_domain"):
            # Blend facilitator override slightly for final result ranking:
            blended_final[domain] = blended[domain] * 0.8 + facilitator_scores[domain] * 0.2
        else:
            blended_final[domain] = blended[domain]

    # Wide stretch-normalization to prevent domain clustering (target 35 to 95)
    max_raw = max(blended_final.values())
    min_raw = min(blended_final.values())
    final_scores = {}
    if max_raw > min_raw:
        target_min = 35.0
        target_max = 95.0
        for domain, raw_val in blended_final.items():
            ratio = (raw_val - min_raw) / (max_raw - min_raw)
            final_scores[domain] = int(round(target_min + ratio * (target_max - target_min)))
    else:
        for domain, raw_val in blended_final.items():
            final_scores[domain] = int(round(raw_val))

    # Sort domains by final stretched score
    sorted_domains = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    top_domain = sorted_domains[0][0] if sorted_domains else "unknown"
    top_3 = [d for d, _ in sorted_domains[:3]]

    # Confidence scoring engine (V5: adjusted by facilitator observation ratings)
    structured_answers = [v for v in responses.values() if isinstance(v, dict)]
    tasks_answered = len(structured_answers)
    
    # 1. Task Completion Rate (max 30 pts)
    task_pts = 30 if tasks_answered >= 20 else 20 if tasks_answered >= 12 else 10 if tasks_answered >= 6 else 5
    
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
    
    # 4. Facilitator Observation Ratings (max 15 pts)
    fac_validation_pts = 0
    obs_avg = 3.0
    if facilitator_note:
        obs_text = facilitator_note.get("observation", "")
        try:
            obs_json = json.loads(obs_text)
            if isinstance(obs_json, dict):
                curiosity = int(obs_json.get("curiosity", 3))
                confidence = int(obs_json.get("confidence", 3))
                focus = int(obs_json.get("focus", 3))
                creativity = int(obs_json.get("creativity", 3))
                communication = int(obs_json.get("communication", 3))
                leadership = int(obs_json.get("leadership", 3))
                persistence = int(obs_json.get("persistence", 3))
                emotional_regulation = int(obs_json.get("emotional_regulation", 3))
                obs_avg = (curiosity + confidence + focus + creativity + communication + leadership + persistence + emotional_regulation) / 8.0
        except Exception:
            # Fallback to direct columns
            obs_avg = (
                (facilitator_note.get("obs_curiosity", 3) or 3) +
                (facilitator_note.get("obs_creativity", 3) or 3) +
                (facilitator_note.get("obs_communication", 3) or 3) +
                (facilitator_note.get("obs_leadership", 3) or 3) +
                (facilitator_note.get("obs_focus", 3) or 3)
            ) / 5.0
        fac_validation_pts = int(round((obs_avg / 5.0) * 15.0))
    
    # 5. Repeated assessment count (max 15 pts)
    repeated_pts = 15 if past_sessions_count >= 2 else 10 if past_sessions_count == 1 else 0

    confidence_score = task_pts + consistency_pts + separation_pts + fac_validation_pts + repeated_pts
    
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
    has_open_ended = any(len(str(combined_res.get(k, "") or "")) > 0 for k in ["reflection_pride", "reflection_flow", "reflection_learning", "reflection_community"])
    
    evidence_sources = {
        "assessment_responses": tasks_answered > 0,
        "open_ended_answers": has_open_ended,
        "facilitator_validation": facilitator_note is not None,
        "repeated_assessments": past_sessions_count > 0
    }

    # Untapped potential
    untapped_potential = []
    for d, score in final_scores.items():
        exp_val = child.get(f"exp_{d}", 0) or 0
        if score >= 75 and exp_val <= 1 and evidence.get(d, {}).get("level") == "Strong":
            untapped_potential.append(d)

    separation_diff = 0
    if len(sorted_domains) > 1:
        separation_diff = sorted_domains[0][1] - sorted_domains[1][1]
    multiple_talents_detected = separation_diff < 5

    eq_val = responses.get("eq_overall", None)
    eq_score = int(round((answer_to_scale(eq_val) / 4.0) * 100)) if eq_val is not None else int(round((final_scores.get("social", 50) + final_scores.get("intrapersonal", 50)) / 2))
    viz_val = responses.get("visualizer_overall", None)
    visualizer_score = int(round((answer_to_scale(viz_val) / 4.0) * 100)) if viz_val is not None else int(round((final_scores.get("creative", 50) + final_scores.get("spatial", 50)) / 2))

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
            db.execute("UPDATE users SET role=?, center_id=?, organization_id=? WHERE id=?", (approved_role, center_id, center["organization_id"], uid))
        else:
            if role != "master_admin":
                db.execute("UPDATE users SET role=?, organization_id=? WHERE id=?", (approved_role, org_id, uid))
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
                
                sync_payload = {
                    "role": approved_role,
                    "is_approved": True
                }
                if center_id:
                    sync_payload["center_id"] = center_id
                    sync_payload["organization_id"] = center["organization_id"]
                elif role != "master_admin":
                    sync_payload["organization_id"] = org_id
                    
                sp_client.table("profiles").update(sync_payload).eq("email", user_row["email"]).execute()
                print(f"[SUPABASE SYNC] Approved user role {approved_role} and synced center/org for {user_row['email']}")
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

    # Facilitators without an assigned org/center see aggregate (master_admin) data
    if role not in ("master_admin", "admin") and (not org_id or not center_id):
        role = "master_admin"

    db = get_db()
    try:
        # 1. Talent Distribution
        if role == "master_admin":
            sessions = db.execute(
                "SELECT top_domain, COUNT(*) as cnt FROM sessions WHERE status='complete' GROUP BY top_domain"
            ).fetchall()
        elif role == "admin":
            sessions = db.execute("""
                SELECT s.top_domain, COUNT(*) as cnt FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=?
                GROUP BY s.top_domain
            """, (org_id,)).fetchall()
        else:
            sessions = db.execute("""
                SELECT s.top_domain, COUNT(*) as cnt FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
                GROUP BY s.top_domain
            """, (org_id, center_id)).fetchall()
        talent_dist = {r["top_domain"]: r["cnt"] for r in sessions if r["top_domain"]}

        # 2. Workshop Demand
        if role == "master_admin":
            workshops = db.execute(
                "SELECT domain, COUNT(*) as cnt FROM workshops GROUP BY domain"
            ).fetchall()
        elif role == "admin":
            workshops = db.execute("""
                SELECT domain, COUNT(*) as cnt FROM workshops WHERE organization_id=? GROUP BY domain
            """, (org_id,)).fetchall()
        else:
            workshops = db.execute("""
                SELECT domain, COUNT(*) as cnt FROM workshops
                WHERE organization_id=? AND center_id=? GROUP BY domain
            """, (org_id, center_id)).fetchall()
        workshop_demand = {r["domain"]: r["cnt"] for r in workshops if r["domain"]}

        # 3. Untapped Potential
        if role == "master_admin":
            sessions_all = db.execute(
                "SELECT child_id, personality_data FROM sessions WHERE status='complete'"
            ).fetchall()
        elif role == "admin":
            sessions_all = db.execute("""
                SELECT s.child_id, s.personality_data FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=?
            """, (org_id,)).fetchall()
        else:
            sessions_all = db.execute("""
                SELECT s.child_id, s.personality_data FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
            """, (org_id, center_id)).fetchall()
        untapped_counts = {}
        for s in sessions_all:
            try:
                pdata = json.loads(s["personality_data"] or "{}")
                for u in pdata.get("untapped_potential", []):
                    untapped_counts[u] = untapped_counts.get(u, 0) + 1
            except Exception:
                pass

        # 4. Growth Data
        if role == "master_admin":
            growth_rows = db.execute(
                "SELECT top_domain, tq_scores, completed_at FROM sessions WHERE status='complete' ORDER BY completed_at"
            ).fetchall()
        elif role == "admin":
            growth_rows = db.execute("""
                SELECT s.top_domain, s.tq_scores, s.completed_at FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=?
                ORDER BY s.completed_at
            """, (org_id,)).fetchall()
        else:
            growth_rows = db.execute("""
                SELECT s.top_domain, s.tq_scores, s.completed_at FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
                ORDER BY s.completed_at
            """, (org_id, center_id)).fetchall()
        growth_data = {}
        for r in growth_rows:
            dom = r["top_domain"]
            if not dom:
                continue
            try:
                tq = json.loads(r["tq_scores"] or "{}")
                score = tq.get(dom, 50)
                date_str = r["completed_at"][:10] if r["completed_at"] else "Unknown"
                growth_data.setdefault(dom, []).append({"date": date_str, "score": score})
            except Exception:
                pass

        # 5. Funnel Totals
        if role == "master_admin":
            total_registered = db.execute("SELECT COUNT(*) FROM children").fetchone()[0]
            total_assessed = db.execute("SELECT COUNT(DISTINCT child_id) FROM sessions WHERE status='complete'").fetchone()[0]
            total_matched = db.execute("SELECT COUNT(*) FROM mentor_matches WHERE status='active'").fetchone()[0]
            total_enrolled = db.execute("SELECT COUNT(DISTINCT child_id) FROM workshop_attendance WHERE status='Present'").fetchone()[0]
        elif role == "admin":
            total_registered = db.execute("SELECT COUNT(*) FROM children WHERE organization_id=?", (org_id,)).fetchone()[0]
            total_assessed = db.execute("""
                SELECT COUNT(DISTINCT s.child_id) FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=?
            """, (org_id,)).fetchone()[0]
            total_matched = db.execute("""
                SELECT COUNT(*) FROM mentor_matches mm
                JOIN children c ON mm.child_id = c.id
                WHERE mm.status='active' AND c.organization_id=?
            """, (org_id,)).fetchone()[0]
            total_enrolled = db.execute("""
                SELECT COUNT(DISTINCT a.child_id) FROM workshop_attendance a
                JOIN children c ON a.child_id = c.id
                WHERE a.status='Present' AND c.organization_id=?
            """, (org_id,)).fetchone()[0]
        else:
            total_registered = db.execute("SELECT COUNT(*) FROM children WHERE organization_id=? AND center_id=?", (org_id, center_id)).fetchone()[0]
            total_assessed = db.execute("""
                SELECT COUNT(DISTINCT s.child_id) FROM sessions s
                JOIN children c ON s.child_id = c.id
                WHERE s.status='complete' AND c.organization_id=? AND c.center_id=?
            """, (org_id, center_id)).fetchone()[0]
            total_matched = db.execute("""
                SELECT COUNT(*) FROM mentor_matches mm
                JOIN children c ON mm.child_id = c.id
                WHERE mm.status='active' AND c.organization_id=? AND c.center_id=?
            """, (org_id, center_id)).fetchone()[0]
            total_enrolled = db.execute("""
                SELECT COUNT(DISTINCT a.child_id) FROM workshop_attendance a
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Analytics query failed: {str(e)}"}), 500

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
            
    # 2. Compile PDF using modular reports builder
    from reports.report_builder import build_pdf_report
    from reports.styles import DOMAINS_MAP
    import json
    from datetime import datetime

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

    report_data = {
        "child": child,
        "session": session,
        "sid": sid,
        "formatted_date": formatted_date,
        "integ": integ,
        "analysis": analysis,
        "sorted_scores": sorted_scores,
        "primary_domain": primary_domain,
        "secondary_domains": secondary_domains,
        "emerging_domains": emerging_domains,
        "untapped_potential": untapped_potential,
        "evidence": evidence,
        "note": note,
        "facilitator_name": facilitator_name,
        "history": history,
        "personalizedSnapshot": personalizedSnapshot
    }

    try:
        pdf_data = build_pdf_report(report_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[PDF ERROR] Failed to build modular PDF report: {e}")
        return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

    return Response(
        pdf_data,
        mimetype="application/pdf",
        headers={"Content-disposition": f"attachment; filename={child['name'].replace(' ', '_')}_GOAT_Talent_Report.pdf"}
    )



# ═══════════════════════════════════════════════════════════════════════════════
# INVENT IT — Performance Evidence Module
# ═══════════════════════════════════════════════════════════════════════════════

import uuid as _uuid

# ── Invent It: SQLite migration helper ───────────────────────────────────────
def _invent_it_init_sqlite():
    """Ensure Invent It tables exist in SQLite fallback DB."""
    try:
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS invent_it_sessions (
                id                        INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id                INTEGER,
                session_uuid              TEXT UNIQUE NOT NULL,
                experience_id             TEXT DEFAULT 'invent_it_v1',
                facilitator_id            INTEGER,
                language                  TEXT DEFAULT 'en',
                status                    TEXT DEFAULT 'in_progress',
                start_ts                  TEXT DEFAULT (datetime('now')),
                end_ts                    TEXT,
                total_duration_ms         INTEGER,
                time_to_first_response_ms INTEGER,
                number_of_ideas           INTEGER DEFAULT 0,
                number_of_submissions     INTEGER DEFAULT 0,
                number_of_revisions       INTEGER DEFAULT 0,
                number_of_voice_responses INTEGER DEFAULT 0,
                number_of_text_responses  INTEGER DEFAULT 0,
                number_of_drawings        INTEGER DEFAULT 0,
                hint_count                INTEGER DEFAULT 0,
                round1_output             TEXT,
                round2_output             TEXT,
                raw_metrics               TEXT,
                created_at                TEXT DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS invent_it_responses (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid     TEXT NOT NULL,
                round_id         INTEGER NOT NULL,
                idea_index       INTEGER,
                input_type       TEXT NOT NULL,
                text_content     TEXT,
                drawing_url      TEXT,
                voice_url        TEXT,
                voice_transcript TEXT,
                language         TEXT,
                duration_ms      INTEGER,
                submitted_at     TEXT DEFAULT (datetime('now')),
                revised          INTEGER DEFAULT 0,
                revision_of      INTEGER
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS invent_it_events (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid TEXT NOT NULL,
                round_id     INTEGER,
                event_type   TEXT NOT NULL,
                event_data   TEXT,
                ts           TEXT DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS invent_it_ai_analysis (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid       TEXT NOT NULL,
                response_id        INTEGER,
                idea_id            TEXT,
                behaviour_evidence TEXT,
                evidence_quality   TEXT,
                reasoning          TEXT,
                model_version      TEXT,
                analysed_at        TEXT DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS invent_it_behaviour_evidence (
                id                       INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid             TEXT UNIQUE NOT NULL,
                o1_score                 REAL,
                o2_score                 REAL,
                o3_score                 REAL,
                o4_score                 REAL,
                o5_score                 REAL,
                o6_score                 REAL,
                provisional_rubric_score INTEGER,
                evidence_confidence      TEXT,
                round1_ideas             INTEGER DEFAULT 0,
                round2_ideas             INTEGER DEFAULT 0,
                cross_round_analysis     TEXT,
                notes                    TEXT,
                computed_at              TEXT DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS invent_it_facilitator_obs (
                id                               INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid                     TEXT NOT NULL,
                facilitator_id                   INTEGER,
                obs_continued_without_prompting  INTEGER DEFAULT -1,
                obs_multiple_ideas               INTEGER DEFAULT -1,
                obs_revised_idea                 INTEGER DEFAULT -1,
                obs_experimented_alternatives    INTEGER DEFAULT -1,
                obs_stuck_after_first            INTEGER DEFAULT -1,
                obs_persisted_after_difficulty   INTEGER DEFAULT -1,
                obs_explained_reasoning          INTEGER DEFAULT -1,
                additional_notes                 TEXT,
                submitted_at                     TEXT DEFAULT (datetime('now'))
            )
        """)
        db.commit()
    except Exception as e:
        print(f"[INVENT IT] SQLite table init warning: {e}")

# ── AI Evidence Classification ────────────────────────────────────────────────
_GEMINI_MODEL = None
_GEMINI_AVAILABLE = False

def _init_gemini():
    global _GEMINI_MODEL, _GEMINI_AVAILABLE
    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            _GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash")
            _GEMINI_AVAILABLE = True
            print("[INVENT IT] Gemini AI classifier initialised.")
        else:
            print("[INVENT IT] No GEMINI_API_KEY found — using heuristic classifier.")
    except ImportError:
        print("[INVENT IT] google-generativeai not installed — using heuristic classifier.")
    except Exception as e:
        print(f"[INVENT IT] Gemini init failed: {e} — using heuristic classifier.")

_init_gemini()

_COMMON_USES_CARDBOARD_BOX = {
    "storage box", "box", "store things", "keep things", "container", "put things in",
    "storage", "keep clothes", "keep books", "trash can", "dustbin", "garbage bin",
    "rakhna", "dabba", "samaan rakhna", "box mein rakhna"
}

def _heuristic_classify(text, round_id):
    """Rule-based fallback classifier returning O1-O6 scores 0-3."""
    if not text or not text.strip():
        return {"O1":0,"O2":0,"O3":0,"O4":0,"O5":0,"O6":0}

    t = text.lower().strip()
    scores = {"O1":0,"O2":0,"O3":0,"O4":0,"O5":0,"O6":0}
    words = set(t.split())

    # O1 — Uncommon Idea Generation
    is_common = any(cu in t for cu in _COMMON_USES_CARDBOARD_BOX)
    if not is_common:
        scores["O1"] = 2
        if len(words) > 15:
            scores["O1"] = 3

    # O2 — Concept Combination (multiple domains mentioned)
    domain_keywords = [
        ["water","liquid","wet","pour","bucket","carry"],
        ["light","lamp","torch","solar","electricity","power"],
        ["music","sound","drum","instrument","beat"],
        ["plant","garden","soil","seed","grow"],
        ["toy","play","game","puppet","robot"],
        ["house","home","shelter","roof","bed"],
        ["chair","seat","sit","furniture","table"],
        ["art","paint","draw","canvas","picture"]
    ]
    domains_hit = sum(1 for kw_list in domain_keywords if any(kw in t for kw in kw_list))
    scores["O2"] = min(domains_hit, 3)

    # O3 — Transformation (modifies or repurposes)
    transform_words = ["turn","make","convert","change","add","attach","connect","combine","fold","cut","paint","decorate","redesign"]
    scores["O3"] = min(sum(1 for w in transform_words if w in t), 3)

    # O4 — Non-obvious approach
    unusual_angles = ["help someone","others","poor","rain","disaster","emergency","solar","tech","digital","robot","smart"]
    scores["O4"] = min(sum(1 for ua in unusual_angles if ua in t), 3)

    # O5 — Independent generation (inferred from idea count — set externally, placeholder here)
    scores["O5"] = 1 if len(words) > 5 else 0

    # O6 — Meaningful novelty = O1 AND has context/usefulness
    useful_words = ["because","so that","can be used","helps","useful","would","could","to carry","to hold","to store","to make"]
    has_usefulness = any(uw in t for uw in useful_words)
    scores["O6"] = min(scores["O1"] + (1 if has_usefulness else 0), 3)

    return scores

def _ai_classify_idea(text, round_id, constraint_text=""):
    """Classify a single idea using Gemini or heuristic fallback."""
    if not text or not text.strip():
        return {
            "O1":0,"O2":0,"O3":0,"O4":0,"O5":0,"O6":0,
            "evidence_quality":"low",
            "reasoning":"Empty response",
            "model":"none"
        }

    if _GEMINI_AVAILABLE and _GEMINI_MODEL:
        try:
            constraint_note = ""
            if round_id == 2 and constraint_text:
                constraint_note = f"\nRound 2 adds this constraint: {constraint_text}"

            prompt = f"""You are a psychometric researcher analysing a child's creative response (ages 10-14).

Task context: The child was shown a cardboard box and asked to invent new uses for it.
Round: {round_id}{constraint_note}

Child's response: "{text}"

Rate each indicator on a 0-3 scale ONLY:
0 = Not present
1 = Emerging / weak
2 = Clear / moderate
3 = Strong / highly evident

Indicators:
O1: Uncommon Idea Generation — does the child move beyond obvious uses (storage, trash can, keeping things)?
O2: Concept Combination — does the child combine the box with unrelated concepts (e.g. solar energy + box = lamp)?
O3: Transformation — does the child meaningfully modify or repurpose rather than just rename?
O4: Non-obvious Approach — does the child come from an unexpected or creative angle?
O5: Independent Generation — does the response show self-driven elaboration without prompting?
O6: Meaningful Novelty — is the idea BOTH unusual AND reasonably meaningful/useful in context?

IMPORTANT RULES:
- A bizarre answer (e.g. "eat the box") is NOT automatically original. Score O6=0 if meaningless.
- Do NOT penalise for limited vocabulary, Hindi words, or simple language.
- Do NOT reward long answers that just list obvious uses.
- Score honestly even if the idea seems simple.

Return ONLY valid JSON, no explanation outside it:
{{"O1":N,"O2":N,"O3":N,"O4":N,"O5":N,"O6":N,"evidence_quality":"high|moderate|low","reasoning":"one sentence"}}"""

            response = _GEMINI_MODEL.generate_content(prompt)
            raw = response.text.strip()
            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^{}]*\}', raw, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["model"] = "gemini-1.5-flash"
                return result
        except Exception as e:
            print(f"[INVENT IT] Gemini classification error: {e}. Falling back to heuristic.")

    # Heuristic fallback
    scores = _heuristic_classify(text, round_id)
    eq = "moderate" if sum(scores.values()) >= 6 else ("low" if sum(scores.values()) <= 2 else "moderate")
    return {**scores, "evidence_quality": eq, "reasoning": "Heuristic classification (AI unavailable)", "model": "heuristic"}

def _compute_behaviour_evidence(session_uuid):
    """Aggregate all AI analyses into provisional rubric + confidence score."""
    db = get_db()
    analyses = db.execute(
        "SELECT behaviour_evidence, evidence_quality, session_uuid FROM invent_it_ai_analysis WHERE session_uuid=?",
        (session_uuid,)
    ).fetchall()

    responses = db.execute(
        "SELECT round_id, input_type FROM invent_it_responses WHERE session_uuid=?",
        (session_uuid,)
    ).fetchall()

    round1_count = sum(1 for r in responses if dict(r)["round_id"] == 1)
    round2_count = sum(1 for r in responses if dict(r)["round_id"] == 2)
    total = len(analyses)

    if total == 0:
        return None

    indicator_sums = {"O1":0,"O2":0,"O3":0,"O4":0,"O5":0,"O6":0}
    indicator_counts = {"O1":0,"O2":0,"O3":0,"O4":0,"O5":0,"O6":0}
    quality_counts = {"high":0,"moderate":0,"low":0}

    for row in analyses:
        d = dict(row)
        be = d.get("behaviour_evidence") or "{}"
        if isinstance(be, str):
            try:
                be = json.loads(be)
            except Exception:
                be = {}
        eq = d.get("evidence_quality", "low")
        quality_counts[eq] = quality_counts.get(eq, 0) + 1
        for k in indicator_sums:
            val = be.get(k.lower(), be.get(k, None))
            if val is not None:
                indicator_sums[k] += int(val)
                indicator_counts[k] += 1

    # Average scores per indicator
    avg = {}
    for k in indicator_sums:
        avg[k] = round(indicator_sums[k] / indicator_counts[k], 2) if indicator_counts[k] > 0 else 0.0

    # Provisional rubric (0-4 scale)
    composite = sum(avg.values()) / 6.0
    if composite >= 2.5:
        rubric = 4
    elif composite >= 1.8:
        rubric = 3
    elif composite >= 1.0:
        rubric = 2
    elif composite >= 0.3:
        rubric = 1
    else:
        rubric = 0

    # Evidence confidence
    if total >= 4 and quality_counts.get("high", 0) >= 2:
        confidence = "high"
    elif total >= 2:
        confidence = "moderate"
    else:
        confidence = "low"

    # O5 — boost if child generated many independent ideas
    if round1_count + round2_count >= 4:
        avg["O5"] = min(avg["O5"] + 1, 3)

    # Cross-round analysis
    round1_analyses = []
    round2_analyses = []
    all_resp = db.execute(
        "SELECT id, round_id, text_content FROM invent_it_responses WHERE session_uuid=?",
        (session_uuid,)
    ).fetchall()
    for r in all_resp:
        rd = dict(r)
        if rd["round_id"] == 1:
            round1_analyses.append(rd.get("text_content",""))
        else:
            round2_analyses.append(rd.get("text_content",""))

    cross = {
        "round1_idea_count": round1_count,
        "round2_idea_count": round2_count,
        "continued_in_round2": round2_count > 0,
        "generated_new_in_round2": round2_count > 0,
        "round2_ideas_sample": round2_analyses[:2]
    }

    return {
        "o1": avg["O1"], "o2": avg["O2"], "o3": avg["O3"],
        "o4": avg["O4"], "o5": avg["O5"], "o6": avg["O6"],
        "provisional_rubric_score": rubric,
        "evidence_confidence": confidence,
        "round1_ideas": round1_count,
        "round2_ideas": round2_count,
        "cross_round_analysis": cross,
        "notes": f"[PROVISIONAL] Based on {total} AI-classified response(s). Rubric not empirically validated. Pilot data required."
    }

# ── Route: Create Game Session ────────────────────────────────────────────────
@app.route("/api/invent-it/sessions", methods=["POST", "OPTIONS"])
def invent_it_create_session():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json or {}
    session_uuid = str(_uuid.uuid4())
    student_id = data.get("student_id")
    language = data.get("language", "en")
    facilitator_id = data.get("facilitator_id")

    try:
        if supabase_client:
            row = supabase_client.table("invent_it_sessions").insert({
                "session_uuid": session_uuid,
                "student_id": student_id,
                "language": language,
                "facilitator_id": facilitator_id,
                "status": "in_progress",
                "experience_id": "invent_it_v1"
            }).execute()
            if row.data:
                return jsonify({"session_uuid": session_uuid, "id": row.data[0].get("id")}), 201
    except Exception as e:
        print(f"[INVENT IT] Supabase create session error: {e}")

    # Fallback to local DB
    _invent_it_init_sqlite()
    db = get_db()
    db.execute("""
        INSERT INTO invent_it_sessions (session_uuid, student_id, language, facilitator_id, status, experience_id)
        VALUES (?,?,?,?,?,?)
    """, (session_uuid, student_id, language, facilitator_id, "in_progress", "invent_it_v1"))
    db.commit()
    return jsonify({"session_uuid": session_uuid}), 201

# ── Route: Submit Response ────────────────────────────────────────────────────
@app.route("/api/invent-it/sessions/<session_uuid>/round/<int:round_id>/response", methods=["POST","OPTIONS"])
def invent_it_submit_response(session_uuid, round_id):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json or {}

    input_type = data.get("input_type", "text")  # text | draw | voice
    text_content = data.get("text_content", "")
    drawing_url = data.get("drawing_url", "")
    voice_url = data.get("voice_url", "")
    voice_transcript = data.get("voice_transcript", "")
    language = data.get("language", "en")
    duration_ms = data.get("duration_ms", 0)
    idea_index = data.get("idea_index", 0)
    revised = bool(data.get("revised", False))
    revision_of = data.get("revision_of")

    resp_data = {
        "session_uuid": session_uuid,
        "round_id": round_id,
        "idea_index": idea_index,
        "input_type": input_type,
        "text_content": text_content,
        "drawing_url": drawing_url,
        "voice_url": voice_url,
        "voice_transcript": voice_transcript,
        "language": language,
        "duration_ms": duration_ms,
        "revised": revised,
        "revision_of": revision_of
    }

    response_id = None
    try:
        if supabase_client:
            row = supabase_client.table("invent_it_responses").insert(resp_data).execute()
            if row.data:
                response_id = row.data[0].get("id")
    except Exception as e:
        print(f"[INVENT IT] Supabase insert response error: {e}")

    if response_id is None:
        db = get_db()
        cur = db.execute("""
            INSERT INTO invent_it_responses
            (session_uuid, round_id, idea_index, input_type, text_content, drawing_url, voice_url, voice_transcript, language, duration_ms, revised, revision_of)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (session_uuid, round_id, idea_index, input_type, text_content, drawing_url, voice_url, voice_transcript, language, duration_ms, int(revised), revision_of))
        db.commit()
        response_id = cur.lastrowid

    # Update session counters
    try:
        update_fields = {}
        if input_type == "text":
            update_fields["number_of_text_responses"] = 1
        elif input_type == "draw":
            update_fields["number_of_drawings"] = 1
        elif input_type == "voice":
            update_fields["number_of_voice_responses"] = 1
        if supabase_client:
            # Increment via RPC isn't easy; we'll do it at complete time
            pass
    except Exception:
        pass

    return jsonify({"response_id": response_id, "status": "saved"}), 201

# ── Route: Log Events ─────────────────────────────────────────────────────────
@app.route("/api/invent-it/sessions/<session_uuid>/events", methods=["POST","OPTIONS"])
def invent_it_log_events(session_uuid):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json or {}
    events = data.get("events", [])
    if not events:
        return jsonify({"status": "no events"}), 200

    saved = 0
    try:
        if supabase_client:
            rows = [{"session_uuid": session_uuid, "round_id": e.get("round_id"), "event_type": e.get("event_type",""), "event_data": e.get("event_data",{})} for e in events]
            supabase_client.table("invent_it_events").insert(rows).execute()
            saved = len(rows)
    except Exception as e:
        print(f"[INVENT IT] Supabase event log error: {e}")

    if saved == 0:
        db = get_db()
        for ev in events:
            db.execute("""
                INSERT INTO invent_it_events (session_uuid, round_id, event_type, event_data)
                VALUES (?,?,?,?)
            """, (session_uuid, ev.get("round_id"), ev.get("event_type",""), json.dumps(ev.get("event_data",{}))))
        db.commit()
        saved = len(events)

    return jsonify({"saved": saved}), 200

# ── Route: Complete Session (triggers AI analysis + metrics) ──────────────────
@app.route("/api/invent-it/sessions/<session_uuid>/complete", methods=["POST","OPTIONS"])
def invent_it_complete_session(session_uuid):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json or {}

    total_duration_ms = data.get("total_duration_ms", 0)
    time_to_first_ms = data.get("time_to_first_response_ms", 0)
    hint_count = data.get("hint_count", 0)
    round1_output = data.get("round1_output", {})
    round2_output = data.get("round2_output", {})

    # Fetch all responses for this session
    responses = []
    try:
        if supabase_client:
            r = supabase_client.table("invent_it_responses").select("*").eq("session_uuid", session_uuid).execute()
            responses = r.data or []
    except Exception as e:
        print(f"[INVENT IT] Supabase fetch responses error: {e}")

    if not responses:
        db = get_db()
        rows = db.execute("SELECT * FROM invent_it_responses WHERE session_uuid=?", (session_uuid,)).fetchall()
        responses = [dict(r) for r in rows]

    # Compute deterministic metrics
    n_text = sum(1 for r in responses if r.get("input_type") == "text")
    n_draw = sum(1 for r in responses if r.get("input_type") == "draw")
    n_voice = sum(1 for r in responses if r.get("input_type") == "voice")
    n_revised = sum(1 for r in responses if r.get("revised") in [True, 1])
    n_total = len(responses)
    r1_count = sum(1 for r in responses if r.get("round_id") == 1)
    r2_count = sum(1 for r in responses if r.get("round_id") == 2)

    raw_metrics = {
        "total_ideas": n_total,
        "round1_ideas": r1_count,
        "round2_ideas": r2_count,
        "number_of_revisions": n_revised,
        "number_of_text_responses": n_text,
        "number_of_drawings": n_draw,
        "number_of_voice_responses": n_voice,
        "hint_count": hint_count,
        "total_duration_ms": total_duration_ms,
        "time_to_first_response_ms": time_to_first_ms
    }

    # AI analysis for each response
    constraint_text = "help someone carry water without spilling it"
    for resp in responses:
        text = resp.get("text_content") or resp.get("voice_transcript") or ""
        if not text.strip():
            continue
        rid = resp.get("round_id", 1)
        resp_id = resp.get("id")

        classification = _ai_classify_idea(text, rid, constraint_text if rid == 2 else "")
        idea_id = f"INV{resp_id or _uuid.uuid4().hex[:6].upper()}"

        be_data = {
            "session_uuid": session_uuid,
            "response_id": resp_id,
            "idea_id": idea_id,
            "behaviour_evidence": {k.lower(): v for k, v in classification.items() if k.startswith("O")},
            "evidence_quality": classification.get("evidence_quality", "low"),
            "reasoning": classification.get("reasoning", ""),
            "model_version": classification.get("model", "heuristic")
        }
        try:
            if supabase_client:
                supabase_client.table("invent_it_ai_analysis").insert({
                    **be_data,
                    "behaviour_evidence": json.dumps(be_data["behaviour_evidence"])
                }).execute()
            else:
                db = get_db()
                db.execute("""
                    INSERT INTO invent_it_ai_analysis
                    (session_uuid, response_id, idea_id, behaviour_evidence, evidence_quality, reasoning, model_version)
                    VALUES (?,?,?,?,?,?,?)
                """, (session_uuid, resp_id, idea_id, json.dumps(be_data["behaviour_evidence"]),
                      be_data["evidence_quality"], be_data["reasoning"], be_data["model_version"]))
                db.commit()
        except Exception as e:
            print(f"[INVENT IT] AI analysis save error: {e}")

    # Compute aggregated behavioural evidence
    be_summary = _compute_behaviour_evidence(session_uuid)

    if be_summary:
        try:
            if supabase_client:
                existing = supabase_client.table("invent_it_behaviour_evidence").select("id").eq("session_uuid", session_uuid).execute()
                be_row = {
                    "session_uuid": session_uuid,
                    "o1_score": be_summary["o1"], "o2_score": be_summary["o2"],
                    "o3_score": be_summary["o3"], "o4_score": be_summary["o4"],
                    "o5_score": be_summary["o5"], "o6_score": be_summary["o6"],
                    "provisional_rubric_score": be_summary["provisional_rubric_score"],
                    "evidence_confidence": be_summary["evidence_confidence"],
                    "round1_ideas": be_summary["round1_ideas"],
                    "round2_ideas": be_summary["round2_ideas"],
                    "cross_round_analysis": json.dumps(be_summary["cross_round_analysis"]),
                    "notes": be_summary["notes"]
                }
                if existing.data:
                    supabase_client.table("invent_it_behaviour_evidence").update(be_row).eq("session_uuid", session_uuid).execute()
                else:
                    supabase_client.table("invent_it_behaviour_evidence").insert(be_row).execute()
            else:
                db = get_db()
                db.execute("""
                    INSERT OR REPLACE INTO invent_it_behaviour_evidence
                    (session_uuid, o1_score, o2_score, o3_score, o4_score, o5_score, o6_score,
                     provisional_rubric_score, evidence_confidence, round1_ideas, round2_ideas,
                     cross_round_analysis, notes)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (session_uuid, be_summary["o1"], be_summary["o2"], be_summary["o3"],
                      be_summary["o4"], be_summary["o5"], be_summary["o6"],
                      be_summary["provisional_rubric_score"], be_summary["evidence_confidence"],
                      be_summary["round1_ideas"], be_summary["round2_ideas"],
                      json.dumps(be_summary["cross_round_analysis"]), be_summary["notes"]))
                db.commit()
        except Exception as e:
            print(f"[INVENT IT] Behaviour evidence save error: {e}")

    # Update session as complete
    update_data = {
        "status": "complete",
        "end_ts": datetime.utcnow().isoformat(),
        "total_duration_ms": total_duration_ms,
        "time_to_first_response_ms": time_to_first_ms,
        "number_of_ideas": n_total,
        "number_of_submissions": n_total,
        "number_of_revisions": n_revised,
        "number_of_text_responses": n_text,
        "number_of_drawings": n_draw,
        "number_of_voice_responses": n_voice,
        "hint_count": hint_count,
        "round1_output": json.dumps(round1_output),
        "round2_output": json.dumps(round2_output),
        "raw_metrics": json.dumps(raw_metrics)
    }
    try:
        if supabase_client:
            supabase_client.table("invent_it_sessions").update(update_data).eq("session_uuid", session_uuid).execute()
        else:
            db = get_db()
            db.execute("""
                UPDATE invent_it_sessions SET
                status=?, end_ts=?, total_duration_ms=?, time_to_first_response_ms=?,
                number_of_ideas=?, number_of_submissions=?, number_of_revisions=?,
                number_of_text_responses=?, number_of_drawings=?, number_of_voice_responses=?,
                hint_count=?, round1_output=?, round2_output=?, raw_metrics=?
                WHERE session_uuid=?
            """, (update_data["status"], update_data["end_ts"], total_duration_ms, time_to_first_ms,
                  n_total, n_total, n_revised, n_text, n_draw, n_voice, hint_count,
                  update_data["round1_output"], update_data["round2_output"], update_data["raw_metrics"],
                  session_uuid))
            db.commit()
    except Exception as e:
        print(f"[INVENT IT] Session complete update error: {e}")

    return jsonify({
        "status": "complete",
        "raw_metrics": raw_metrics,
        "behaviour_evidence": be_summary,
        "session_uuid": session_uuid
    }), 200

# ── Route: Get Session ────────────────────────────────────────────────────────
@app.route("/api/invent-it/sessions/<session_uuid>", methods=["GET"])
def invent_it_get_session(session_uuid):
    session = None
    try:
        if supabase_client:
            r = supabase_client.table("invent_it_sessions").select("*").eq("session_uuid", session_uuid).execute()
            if r.data:
                session = r.data[0]
    except Exception as e:
        print(f"[INVENT IT] Get session error: {e}")

    if not session:
        db = get_db()
        row = db.execute("SELECT * FROM invent_it_sessions WHERE session_uuid=?", (session_uuid,)).fetchone()
        if row:
            session = dict(row)

    if not session:
        return jsonify({"error": "Session not found"}), 404

    return jsonify(session), 200

# ── Route: Facilitator Observation ────────────────────────────────────────────
@app.route("/api/invent-it/sessions/<session_uuid>/facilitator-observation", methods=["POST","OPTIONS"])
def invent_it_facilitator_obs(session_uuid):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    user = current_user()
    data = request.json or {}

    obs_data = {
        "session_uuid": session_uuid,
        "facilitator_id": user["id"] if user else None,
        "obs_continued_without_prompting": data.get("obs_continued_without_prompting", -1),
        "obs_multiple_ideas": data.get("obs_multiple_ideas", -1),
        "obs_revised_idea": data.get("obs_revised_idea", -1),
        "obs_experimented_alternatives": data.get("obs_experimented_alternatives", -1),
        "obs_stuck_after_first": data.get("obs_stuck_after_first", -1),
        "obs_persisted_after_difficulty": data.get("obs_persisted_after_difficulty", -1),
        "obs_explained_reasoning": data.get("obs_explained_reasoning", -1),
        "additional_notes": data.get("additional_notes", "")
    }

    try:
        if supabase_client:
            supabase_client.table("invent_it_facilitator_obs").insert(obs_data).execute()
            return jsonify({"status": "saved"}), 201
    except Exception as e:
        print(f"[INVENT IT] Facilitator obs save error: {e}")

    db = get_db()
    db.execute("""
        INSERT INTO invent_it_facilitator_obs
        (session_uuid, facilitator_id, obs_continued_without_prompting, obs_multiple_ideas,
         obs_revised_idea, obs_experimented_alternatives, obs_stuck_after_first,
         obs_persisted_after_difficulty, obs_explained_reasoning, additional_notes)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (session_uuid, obs_data["facilitator_id"],
          obs_data["obs_continued_without_prompting"], obs_data["obs_multiple_ideas"],
          obs_data["obs_revised_idea"], obs_data["obs_experimented_alternatives"],
          obs_data["obs_stuck_after_first"], obs_data["obs_persisted_after_difficulty"],
          obs_data["obs_explained_reasoning"], obs_data["additional_notes"]))
    db.commit()
    return jsonify({"status": "saved"}), 201

# ── Route: Admin — List Sessions ──────────────────────────────────────────────
@app.route("/api/invent-it/admin/sessions", methods=["GET"])
def invent_it_admin_sessions():
    user, error = require_user()
    if error:
        return error
    if user.get("role") not in ("master_admin", "admin", "facilitator"):
        return jsonify({"error": "Forbidden"}), 403

    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    offset = (page - 1) * limit

    sessions = []
    try:
        if supabase_client:
            q = supabase_client.table("invent_it_sessions").select(
                "id, session_uuid, student_id, language, status, start_ts, end_ts, number_of_ideas, evidence_confidence:invent_it_behaviour_evidence(evidence_confidence)"
            ).order("created_at", desc=True).range(offset, offset + limit - 1)
            r = supabase_client.table("invent_it_sessions").select("*").order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            sessions = r.data or []
    except Exception as e:
        print(f"[INVENT IT] Admin sessions error: {e}")

    if not sessions:
        db = get_db()
        rows = db.execute("""
            SELECT s.*, be.evidence_confidence, be.provisional_rubric_score
            FROM invent_it_sessions s
            LEFT JOIN invent_it_behaviour_evidence be ON be.session_uuid = s.session_uuid
            ORDER BY s.created_at DESC LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        sessions = [dict(r) for r in rows]

    return jsonify({"sessions": sessions, "page": page, "limit": limit}), 200

# ── Route: Admin — Research View ──────────────────────────────────────────────
@app.route("/api/invent-it/admin/sessions/<session_uuid>/research", methods=["GET"])
def invent_it_research_view(session_uuid):
    user, error = require_user()
    if error:
        return error
    if user.get("role") not in ("master_admin", "admin"):
        return jsonify({"error": "Forbidden — Research Mode requires admin access"}), 403

    result = {}

    def _fetch(table, field="session_uuid"):
        try:
            if supabase_client:
                r = supabase_client.table(table).select("*").eq(field, session_uuid).execute()
                return r.data or []
        except Exception as e:
            print(f"[INVENT IT] Research fetch {table} error: {e}")
        db = get_db()
        rows = db.execute(f"SELECT * FROM {table} WHERE {field}=?", (session_uuid,)).fetchall()
        return [dict(r) for r in rows]

    result["session"] = (_fetch("invent_it_sessions") or [{}])[0]
    result["responses"] = _fetch("invent_it_responses")
    result["events"] = _fetch("invent_it_events")
    result["ai_analysis"] = _fetch("invent_it_ai_analysis")
    result["behaviour_evidence"] = (_fetch("invent_it_behaviour_evidence") or [{}])[0]
    result["facilitator_observations"] = _fetch("invent_it_facilitator_obs")

    # Attach child info if available
    student_id = result["session"].get("student_id")
    if student_id:
        try:
            db = get_db()
            child = db.execute("SELECT id, name, age, gender, school_year FROM children WHERE id=?", (student_id,)).fetchone()
            result["child"] = dict(child) if child else {}
        except Exception:
            result["child"] = {}

    return jsonify(result), 200

# ── Route: Hint usage update ──────────────────────────────────────────────────
@app.route("/api/invent-it/sessions/<session_uuid>/hint", methods=["POST","OPTIONS"])
def invent_it_hint(session_uuid):
    if request.method == "OPTIONS":
        return jsonify({}), 200
    try:
        if supabase_client:
            r = supabase_client.table("invent_it_sessions").select("hint_count").eq("session_uuid", session_uuid).execute()
            current = (r.data or [{}])[0].get("hint_count", 0)
            supabase_client.table("invent_it_sessions").update({"hint_count": current + 1}).eq("session_uuid", session_uuid).execute()
        else:
            db = get_db()
            db.execute("UPDATE invent_it_sessions SET hint_count = hint_count + 1 WHERE session_uuid=?", (session_uuid,))
            db.commit()
    except Exception as e:
        print(f"[INVENT IT] Hint update error: {e}")
    return jsonify({"status": "ok"}), 200



# ═══════════════════════════════════════════════════════════════════════════════
# ARTSPARK — Gamified Adaptive Psychometric Module (Creative & Artistic)
# ═══════════════════════════════════════════════════════════════════════════════
#
# Architecture:
#   • Item bank: artspark_item_bank — 6 domains × 4 difficulty tiers
#   • Session:   artspark_sessions  — tracks theta estimates, XP, medals, trail
#   • Response:  artspark_responses — per-question answer log
#
# Adaptive algorithm: IRT-lite (1-parameter logistic approximation)
#   θ ← θ + 0.4 × (correct - P(correct))
#   P(correct) = 1 / (1 + exp(-1.7 × (θ - b)))   where b = item difficulty
# ═══════════════════════════════════════════════════════════════════════════════

import math as _math

_ARTSPARK_DOMAINS   = ["visual_art","music","storytelling","drama","dance_movement","craft_design"]
_ARTSPARK_TIERS     = {"easy":(-2.0,-0.5),"medium":(-0.5,0.5),"hard":(0.5,1.5),"expert":(1.5,2.5)}
_ARTSPARK_MAX_Q     = 12   # questions per domain before session auto-completes
_ARTSPARK_SE_CUTOFF = 0.30 # standard error convergence threshold (stops early)

# ── Medal thresholds (theta) ──────────────────────────────────────────────────
def _artspark_medal(theta):
    if theta is None:
        return "none"
    if theta >= 1.5:
        return "platinum"
    if theta >= 0.8:
        return "gold"
    if theta >= 0.1:
        return "silver"
    if theta >= -0.5:
        return "bronze"
    return "none"

# ── IRT 1PL probability ───────────────────────────────────────────────────────
def _artspark_p_correct(theta, b):
    return 1.0 / (1.0 + _math.exp(-1.7 * (theta - b)))

# ── Theta update ──────────────────────────────────────────────────────────────
def _artspark_update_theta(theta, b, correct):
    """1PL EAP-lite update: move theta toward the ability implied by the response."""
    p = _artspark_p_correct(theta, b)
    delta = 0.4 * ((1 if correct else 0) - p)
    new_theta = max(-3.0, min(3.0, theta + delta))
    return round(new_theta, 4)

# ── Standard error estimate ───────────────────────────────────────────────────
def _artspark_se(theta, answered_bs):
    """Approx Fisher information sum for SE calculation."""
    if not answered_bs:
        return 99.0
    info = sum(_artspark_p_correct(theta, b) * (1 - _artspark_p_correct(theta, b)) for b in answered_bs)
    return round(1.0 / _math.sqrt(max(info, 0.0001)), 4)

# ── XP calculation ────────────────────────────────────────────────────────────
def _artspark_xp(is_correct, tier, streak):
    base     = {"easy":10,"medium":20,"hard":35,"expert":50}.get(tier, 15)
    bonus    = base if is_correct else 0
    streak_b = min(streak, 5) * 5  # +5 XP per streak level, capped at +25
    return base + bonus + streak_b

# ── Next question selector ─────────────────────────────────────────────────────
def _artspark_next_question(theta, domain, answered_uuids, db):
    """
    Select the next item from the bank closest to the current theta,
    excluding already-answered items and preferring the matching difficulty tier.
    """
    target_b = theta  # target difficulty = current ability estimate

    if supabase_client:
        try:
            r = supabase_client.table("artspark_item_bank")\
                .select("*")\
                .eq("domain", domain)\
                .eq("active", 1)\
                .execute()
            rows = r.data or []
        except Exception as e:
            print(f"[ARTSPARK] Supabase item fetch error: {e}")
            rows = []
        if not rows:
            # Fallback to SQLite
            rows = [dict(r) for r in db.execute(
                "SELECT * FROM artspark_item_bank WHERE domain=? AND active=1", (domain,)
            ).fetchall()]
    else:
        rows = [dict(r) for r in db.execute(
            "SELECT * FROM artspark_item_bank WHERE domain=? AND active=1", (domain,)
        ).fetchall()]

    # Filter out already-answered
    candidates = [r for r in rows if r["item_uuid"] not in answered_uuids]
    if not candidates:
        return None

    # Pick the item with difficulty closest to theta
    best = min(candidates, key=lambda r: abs(r["difficulty"] - target_b))
    return best

# ── SQLite table init ──────────────────────────────────────────────────────────
def _artspark_init_sqlite():
    """Ensure ArtSpark tables exist in SQLite fallback DB."""
    try:
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS artspark_item_bank (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                item_uuid   TEXT UNIQUE NOT NULL,
                domain      TEXT NOT NULL,
                tier        TEXT NOT NULL,
                difficulty  REAL NOT NULL DEFAULT 0.0,
                q_type      TEXT NOT NULL,
                prompt      TEXT NOT NULL,
                options     TEXT,
                correct_key TEXT,
                explanation TEXT,
                tags        TEXT,
                language    TEXT DEFAULT 'en',
                active      INTEGER DEFAULT 1,
                created_at  TEXT DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS artspark_sessions (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid        TEXT UNIQUE NOT NULL,
                child_id            INTEGER,
                student_id          INTEGER,
                facilitator_id      INTEGER,
                language            TEXT DEFAULT 'en',
                status              TEXT DEFAULT 'in_progress',
                domain_order        TEXT,
                current_domain_idx  INTEGER DEFAULT 0,
                current_q_idx       INTEGER DEFAULT 0,
                theta               TEXT DEFAULT '{}',
                medals              TEXT DEFAULT '{}',
                xp_total            INTEGER DEFAULT 0,
                streak_max          INTEGER DEFAULT 0,
                questions_answered  INTEGER DEFAULT 0,
                raw_item_trail      TEXT DEFAULT '[]',
                start_ts            TEXT DEFAULT (datetime('now')),
                end_ts              TEXT,
                total_duration_ms   INTEGER,
                created_at          TEXT DEFAULT (datetime('now'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS artspark_responses (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_uuid    TEXT NOT NULL,
                item_uuid       TEXT NOT NULL,
                domain          TEXT NOT NULL,
                tier            TEXT NOT NULL,
                difficulty      REAL,
                q_type          TEXT,
                response_value  TEXT,
                is_correct      INTEGER,
                response_ms     INTEGER,
                theta_before    REAL,
                theta_after     REAL,
                xp_earned       INTEGER DEFAULT 0,
                submitted_at    TEXT DEFAULT (datetime('now'))
            )
        """)
        db.commit()
        print("[ARTSPARK] SQLite tables initialised.")
    except Exception as e:
        print(f"[ARTSPARK] SQLite init warning: {e}")

# ── Helper: read/write session ─────────────────────────────────────────────────
def _artspark_get_session(session_uuid, db):
    if supabase_client:
        try:
            r = supabase_client.table("artspark_sessions").select("*").eq("session_uuid", session_uuid).execute()
            if r.data:
                return r.data[0]
        except Exception:
            pass
    row = db.execute("SELECT * FROM artspark_sessions WHERE session_uuid=?", (session_uuid,)).fetchone()
    return dict(row) if row else None

def _artspark_update_session(session_uuid, fields, db):
    if supabase_client:
        try:
            supabase_client.table("artspark_sessions").update(fields).eq("session_uuid", session_uuid).execute()
            return
        except Exception as e:
            print(f"[ARTSPARK] Supabase session update error: {e}")
    cols  = ", ".join(f"{k}=?" for k in fields)
    vals  = list(fields.values()) + [session_uuid]
    db.execute(f"UPDATE artspark_sessions SET {cols} WHERE session_uuid=?", vals)
    db.commit()

# ══ Route: Create Session ══════════════════════════════════════════════════════
@app.route("/api/artspark/sessions", methods=["POST","OPTIONS"])
def artspark_create_session():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data         = request.json or {}
    child_id     = data.get("child_id")
    student_id   = data.get("student_id") or child_id
    language     = data.get("language", "en")
    domains      = data.get("domains", _ARTSPARK_DOMAINS[:])
    facilitator_id = None

    # Optional auth (session can be anonymous like Invent It)
    try:
        user, _ = require_user()
        if user:
            facilitator_id = user.get("id")
    except Exception:
        pass

    session_uuid  = str(_uuid.uuid4())
    theta_init    = json.dumps({d: 0.0 for d in domains})
    medals_init   = json.dumps({d: "none" for d in domains})
    domain_order  = json.dumps(domains)

    record = {
        "session_uuid":     session_uuid,
        "child_id":         child_id,
        "student_id":       student_id,
        "facilitator_id":   facilitator_id,
        "language":         language,
        "status":           "in_progress",
        "domain_order":     domain_order,
        "current_domain_idx": 0,
        "current_q_idx":    0,
        "theta":            theta_init,
        "medals":           medals_init,
        "xp_total":         0,
        "streak_max":       0,
        "questions_answered": 0,
        "raw_item_trail":   "[]",
    }

    if supabase_client:
        try:
            supabase_client.table("artspark_sessions").insert(record).execute()
        except Exception as e:
            print(f"[ARTSPARK] Supabase create session error: {e}")
    db = get_db()
    try:
        db.execute("""
            INSERT OR IGNORE INTO artspark_sessions
            (session_uuid,child_id,student_id,facilitator_id,language,status,
             domain_order,current_domain_idx,current_q_idx,theta,medals,
             xp_total,streak_max,questions_answered,raw_item_trail)
            VALUES (?,?,?,?,?,?,?,0,0,?,?,0,0,0,'[]')
        """, (session_uuid, child_id, student_id, facilitator_id, language,
              "in_progress", domain_order, theta_init, medals_init))
        db.commit()
    except Exception as e:
        print(f"[ARTSPARK] SQLite create session error: {e}")

    # Fetch first question
    domains_list = json.loads(domain_order)
    domain       = domains_list[0]
    theta_map    = json.loads(theta_init)
    theta        = theta_map.get(domain, 0.0)
    first_item   = _artspark_next_question(theta, domain, set(), db)

    return jsonify({
        "session_uuid":    session_uuid,
        "domain":          domain,
        "domain_idx":      0,
        "q_idx":           0,
        "domains":         domains_list,
        "xp_total":        0,
        "streak":          0,
        "theta":           theta_map,
        "next_question":   _artspark_format_item(first_item),
    }), 201


# ── Helper: strip correct_key before sending to client ───────────────────────
def _artspark_format_item(item):
    if not item:
        return None
    safe = {k: v for k, v in item.items() if k not in ("correct_key","explanation")}
    # Parse options JSON string to list/dict
    if safe.get("options") and isinstance(safe["options"], str):
        try:
            safe["options"] = json.loads(safe["options"])
        except Exception:
            pass
    if safe.get("tags") and isinstance(safe["tags"], str):
        try:
            safe["tags"] = json.loads(safe["tags"])
        except Exception:
            pass
    return safe


# ══ Route: Get Session State ═══════════════════════════════════════════════════
@app.route("/api/artspark/sessions/<session_uuid>", methods=["GET"])
def artspark_get_session(session_uuid):
    db  = get_db()
    sess = _artspark_get_session(session_uuid, db)
    if not sess:
        return jsonify({"error": "Session not found"}), 404

    domains      = json.loads(sess.get("domain_order") or "[]")
    theta_map    = json.loads(sess.get("theta") or "{}")
    medals_map   = json.loads(sess.get("medals") or "{}")
    trail        = json.loads(sess.get("raw_item_trail") or "[]")
    answered_ids = {t["item_uuid"] for t in trail}
    dom_idx      = int(sess.get("current_domain_idx", 0))
    domain       = domains[dom_idx] if dom_idx < len(domains) else None
    theta        = theta_map.get(domain, 0.0) if domain else 0.0
    next_item    = _artspark_next_question(theta, domain, answered_ids, db) if domain else None

    return jsonify({
        "session_uuid":      session_uuid,
        "status":            sess.get("status"),
        "domains":           domains,
        "current_domain":    domain,
        "domain_idx":        dom_idx,
        "q_idx":             int(sess.get("current_q_idx", 0)),
        "theta":             theta_map,
        "medals":            medals_map,
        "xp_total":          int(sess.get("xp_total", 0)),
        "streak_max":        int(sess.get("streak_max", 0)),
        "questions_answered":int(sess.get("questions_answered", 0)),
        "next_question":     _artspark_format_item(next_item),
    }), 200


# ══ Route: Submit Response → Get Next Adaptive Question ════════════════════════
@app.route("/api/artspark/sessions/<session_uuid>/respond", methods=["POST","OPTIONS"])
def artspark_respond(session_uuid):
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data          = request.json or {}
    item_uuid     = data.get("item_uuid")
    response_val  = data.get("response_value", "")
    response_ms   = int(data.get("response_ms", 0))

    if not item_uuid:
        return jsonify({"error": "item_uuid required"}), 400

    db   = get_db()
    sess = _artspark_get_session(session_uuid, db)
    if not sess:
        return jsonify({"error": "Session not found"}), 404
    if sess.get("status") == "completed":
        return jsonify({"error": "Session already completed"}), 400

    # ── Fetch item from bank ──────────────────────────────────────────────────
    item = None
    if supabase_client:
        try:
            r = supabase_client.table("artspark_item_bank").select("*").eq("item_uuid", item_uuid).execute()
            if r.data:
                item = r.data[0]
        except Exception:
            pass
    if not item:
        row = db.execute("SELECT * FROM artspark_item_bank WHERE item_uuid=?", (item_uuid,)).fetchone()
        if row:
            item = dict(row)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    domain      = item["domain"]
    tier        = item["tier"]
    b           = float(item["difficulty"])
    q_type      = item["q_type"]
    correct_key = item.get("correct_key")

    # ── Score the response ────────────────────────────────────────────────────
    if q_type in ("image_choice","sequence") and correct_key:
        # sequence: correct_key is JSON array, response_value must match
        if q_type == "sequence":
            try:
                correct_list = json.loads(correct_key) if isinstance(correct_key, str) else correct_key
                resp_list    = json.loads(response_val) if isinstance(response_val, str) else response_val
                is_correct   = (resp_list == correct_list)
            except Exception:
                is_correct = False
        else:
            is_correct = (str(response_val).strip().upper() == str(correct_key).strip().upper())
        is_correct_int = 1 if is_correct else 0
    elif q_type == "likert":
        is_correct     = None   # open-ended
        is_correct_int = None
        is_correct     = None
    else:
        is_correct     = None   # open_text: human-scored
        is_correct_int = None

    # ── Update theta ──────────────────────────────────────────────────────────
    theta_map    = json.loads(sess.get("theta") or "{}")
    theta_before = theta_map.get(domain, 0.0)

    if is_correct is not None:
        theta_after = _artspark_update_theta(theta_before, b, is_correct)
    else:
        # Likert / open_text: soft nudge based on engagement (response length)
        engagement = min(len(str(response_val)), 200) / 200.0  # 0..1
        theta_after = round(min(theta_before + 0.1 * engagement, 3.0), 4)

    theta_map[domain] = theta_after

    # ── XP + streak ───────────────────────────────────────────────────────────
    trail        = json.loads(sess.get("raw_item_trail") or "[]")
    # Streak: count consecutive correct answers in this domain
    domain_trail = [t for t in trail if t.get("domain") == domain]
    streak       = 0
    for t in reversed(domain_trail):
        if t.get("correct") is True:
            streak += 1
        else:
            break

    xp_earned = _artspark_xp(bool(is_correct), tier, streak)
    new_xp    = int(sess.get("xp_total", 0)) + xp_earned

    if is_correct:
        streak += 1
    else:
        streak = 0

    new_streak_max = max(int(sess.get("streak_max", 0)), streak)

    # ── Append to item trail ──────────────────────────────────────────────────
    trail.append({
        "item_uuid":  item_uuid,
        "domain":     domain,
        "tier":       tier,
        "b":          b,
        "response":   str(response_val)[:500],
        "correct":    is_correct,
        "theta_after":theta_after,
        "xp":         xp_earned,
    })

    # ── Persist response row ──────────────────────────────────────────────────
    resp_record = {
        "session_uuid":  session_uuid,
        "item_uuid":     item_uuid,
        "domain":        domain,
        "tier":          tier,
        "difficulty":    b,
        "q_type":        q_type,
        "response_value":str(response_val)[:1000],
        "is_correct":    is_correct_int,
        "response_ms":   response_ms,
        "theta_before":  theta_before,
        "theta_after":   theta_after,
        "xp_earned":     xp_earned,
    }
    if supabase_client:
        try:
            supabase_client.table("artspark_responses").insert(resp_record).execute()
        except Exception as e:
            print(f"[ARTSPARK] Supabase response insert error: {e}")
    try:
        db.execute("""
            INSERT INTO artspark_responses
            (session_uuid,item_uuid,domain,tier,difficulty,q_type,response_value,
             is_correct,response_ms,theta_before,theta_after,xp_earned)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (session_uuid, item_uuid, domain, tier, b, q_type,
              str(response_val)[:1000], is_correct_int, response_ms,
              theta_before, theta_after, xp_earned))
        db.commit()
    except Exception as e:
        print(f"[ARTSPARK] SQLite response insert error: {e}")

    # ── Determine next question / domain advance ──────────────────────────────
    domains      = json.loads(sess.get("domain_order") or "[]")
    dom_idx      = int(sess.get("current_domain_idx", 0))
    q_idx        = int(sess.get("current_q_idx", 0)) + 1
    q_answered   = int(sess.get("questions_answered", 0)) + 1

    answered_uuids = {t["item_uuid"] for t in trail}
    domain_answered_bs = [t["b"] for t in trail if t["domain"] == domain]
    se = _artspark_se(theta_after, domain_answered_bs)

    # Advance domain if max questions reached or SE converged
    domain_q_count = len([t for t in trail if t["domain"] == domain])
    advance_domain = (domain_q_count >= _ARTSPARK_MAX_Q) or (se <= _ARTSPARK_SE_CUTOFF)
    level_up       = False

    if advance_domain:
        dom_idx += 1
        q_idx    = 0

    # Detect tier level-up for gamification feedback
    tier_before = "easy"
    for t_name, (lo, hi) in _ARTSPARK_TIERS.items():
        if lo <= theta_before < hi:
            tier_before = t_name
    tier_after = "easy"
    for t_name, (lo, hi) in _ARTSPARK_TIERS.items():
        if lo <= theta_after < hi:
            tier_after = t_name
    tier_order = ["easy","medium","hard","expert"]
    if tier_order.index(tier_after) > tier_order.index(tier_before):
        level_up = True

    # Completed all domains?
    session_complete = (dom_idx >= len(domains))

    next_item = None
    next_domain = None
    if not session_complete:
        next_domain = domains[dom_idx]
        next_theta  = theta_map.get(next_domain, 0.0)
        next_item   = _artspark_next_question(next_theta, next_domain, answered_uuids, db)

    # ── Update session ────────────────────────────────────────────────────────
    medals_map = json.loads(sess.get("medals") or "{}")
    medals_map[domain] = _artspark_medal(theta_after)

    update_fields = {
        "theta":            json.dumps(theta_map),
        "medals":           json.dumps(medals_map),
        "xp_total":         new_xp,
        "streak_max":       new_streak_max,
        "questions_answered": q_answered,
        "raw_item_trail":   json.dumps(trail),
        "current_domain_idx": dom_idx,
        "current_q_idx":    q_idx,
    }
    if session_complete:
        update_fields["status"]  = "completed"
        update_fields["end_ts"]  = datetime.utcnow().isoformat()
    _artspark_update_session(session_uuid, update_fields, db)

    return jsonify({
        "scored":         is_correct,
        "xp_earned":      xp_earned,
        "xp_total":       new_xp,
        "streak":         streak,
        "streak_max":     new_streak_max,
        "level_up":       level_up,
        "tier_after":     tier_after,
        "theta":          theta_map,
        "medals":         medals_map,
        "domain":         next_domain,
        "domain_idx":     dom_idx,
        "q_idx":          q_idx,
        "session_complete": session_complete,
        "next_question":  _artspark_format_item(next_item),
        "explanation":    item.get("explanation") if is_correct is not None else None,
    }), 200


# ══ Route: Complete Session ════════════════════════════════════════════════════
@app.route("/api/artspark/sessions/<session_uuid>/complete", methods=["POST","OPTIONS"])
def artspark_complete_session(session_uuid):
    if request.method == "OPTIONS":
        return jsonify({}), 200

    db   = get_db()
    sess = _artspark_get_session(session_uuid, db)
    if not sess:
        return jsonify({"error": "Session not found"}), 404

    theta_map   = json.loads(sess.get("theta") or "{}")
    medals_map  = {d: _artspark_medal(t) for d, t in theta_map.items()}
    xp_total    = int(sess.get("xp_total", 0))
    streak_max  = int(sess.get("streak_max", 0))
    trail       = json.loads(sess.get("raw_item_trail") or "[]")

    # Domain summary
    domain_summary = {}
    for d in json.loads(sess.get("domain_order") or "[]"):
        d_trail = [t for t in trail if t["domain"] == d]
        domain_summary[d] = {
            "theta":        round(theta_map.get(d, 0.0), 3),
            "medal":        medals_map.get(d, "none"),
            "questions":    len(d_trail),
            "correct":      sum(1 for t in d_trail if t.get("correct") is True),
        }

    update_fields = {
        "status":  "completed",
        "end_ts":  datetime.utcnow().isoformat(),
        "medals":  json.dumps(medals_map),
    }
    _artspark_update_session(session_uuid, update_fields, db)

    return jsonify({
        "session_uuid":   session_uuid,
        "status":         "completed",
        "theta":          theta_map,
        "medals":         medals_map,
        "xp_total":       xp_total,
        "streak_max":     streak_max,
        "domain_summary": domain_summary,
        "questions_answered": int(sess.get("questions_answered", 0)),
    }), 200


# ══ Route: Admin — List Sessions ═══════════════════════════════════════════════
@app.route("/api/artspark/admin/sessions", methods=["GET"])
def artspark_admin_sessions():
    user, error = require_user()
    if error:
        return error
    if user.get("role") not in ("master_admin", "admin"):
        return jsonify({"error": "Forbidden"}), 403

    page  = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 50))
    offset = (page - 1) * limit

    sessions = []
    if supabase_client:
        try:
            r = supabase_client.table("artspark_sessions")\
                .select("*")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            sessions = r.data or []
        except Exception as e:
            print(f"[ARTSPARK] Admin list error: {e}")

    if not sessions:
        db = get_db()
        rows = db.execute(
            "SELECT * FROM artspark_sessions ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        ).fetchall()
        sessions = [dict(r) for r in rows]

    return jsonify({"sessions": sessions, "page": page, "limit": limit}), 200


# ══ ArtSpark SQLite init (called inside init_db) ════════════════════════════
_artspark_init_sqlite()


# Initialize database on import (Gunicorn/production compatibility)
init_db()

if __name__ == "__main__":
    print("\n[SUCCESS] GOAT backend running at http://localhost:5050\n")
    app.run(port=5050, debug=True, use_reloader=False)
