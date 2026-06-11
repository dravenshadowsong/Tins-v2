import os
import json
import sqlite3
from dotenv import load_dotenv

load_dotenv()

# Automatically rewrite DATABASE_URL if present to match server.py's logic
db_url = os.environ.get("DATABASE_URL")
if db_url and "db.ubsjcfaokemckctswnzi.supabase.co" in db_url:
    import re
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    match = re.search(r"postgresql://postgres:([^@]+)@db\.ubsjcfaokemckctswnzi\.supabase\.co:5432/(.+)", db_url)
    if match:
        password = match.group(1)
        dbname = match.group(2)
        project_ref = "ubsjcfaokemckctswnzi"
        pooler_host = "aws-1-ap-southeast-2.pooler.supabase.com"
        pooler_port = 6543
        
        access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
        if access_token:
            try:
                import urllib.request
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
            except Exception as api_err:
                print(f"[WARNING] Failed to dynamically fetch pooler configuration: {api_err}")
        
        rewritten_url = f"postgresql://postgres.{project_ref}:{password}@{pooler_host}:{pooler_port}/{dbname}"
        db_url = rewritten_url
        print(f"[INFO] Rewrote DATABASE_URL for connection pooling.")

def seed_puzzles():
    # Load extended bank JSON
    bank_path = os.path.join(os.path.dirname(__file__), "question_bank", "extended_bank.json")
    if not os.path.exists(bank_path):
        print(f"[ERROR] question bank file not found at {bank_path}")
        return
        
    with open(bank_path, "r", encoding="utf-8") as f:
        puzzles = json.load(f)
        
    print(f"Loaded {len(puzzles)} puzzles from JSON. Starting seeding process...")

    # 1. Seed SQLite (goat.db)
    sqlite_db_path = os.path.join(os.path.dirname(__file__), "goat.db")
    print(f"Connecting to SQLite: {sqlite_db_path}")
    try:
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Clear existing puzzles to ensure a clean sync
        sqlite_cursor.execute("DELETE FROM puzzles")
        
        for p in puzzles:
            sqlite_cursor.execute("""
                INSERT OR REPLACE INTO puzzles (key, type, domain, component, data)
                VALUES (?, ?, ?, ?, ?)
            """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
            
        sqlite_conn.commit()
        sqlite_conn.close()
        print("[SUCCESS] Local SQLite puzzles table seeded successfully.")
    except Exception as sqlite_err:
        print(f"[ERROR] Failed to seed local SQLite database: {sqlite_err}")

    # 2. Seed Postgres / Supabase
    if db_url:
        print("Connecting to Supabase Postgres...")
        # Parse connection details to print for debugging
        try:
            # Simple password mask
            masked_url = db_url
            if "@" in db_url:
                prefix, suffix = db_url.split("@", 1)
                if ":" in prefix:
                    parts = prefix.split(":")
                    if len(parts) > 2:
                        masked_url = ":".join(parts[:-1]) + ":****@" + suffix
            print(f"[DEBUG] Connection URI: {masked_url}")
        except Exception:
            pass

        try:
            import psycopg2
            pg_conn = psycopg2.connect(db_url, connect_timeout=10)
            pg_cursor = pg_conn.cursor()
            
            # Clear existing puzzles in Postgres
            pg_cursor.execute("DELETE FROM puzzles")
            
            for p in puzzles:
                pg_cursor.execute("""
                    INSERT INTO puzzles (key, type, domain, component, data)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE 
                    SET type = EXCLUDED.type, domain = EXCLUDED.domain, component = EXCLUDED.component, data = EXCLUDED.data
                """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
                
            pg_conn.commit()
            pg_cursor.close()
            pg_conn.close()
            print("[SUCCESS] Supabase Postgres puzzles table seeded successfully.")
        except ImportError:
            print("[WARNING] psycopg2 is not installed. Skipping Postgres seeding.")
        except Exception as pg_err:
            print(f"[ERROR] Failed to seed Supabase Postgres database: {pg_err}")
    else:
        print("[INFO] DATABASE_URL not configured. Skipping remote Postgres seeding.")

if __name__ == "__main__":
    seed_puzzles()
