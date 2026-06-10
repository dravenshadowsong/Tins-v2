import os
import requests
import sqlite3
import sys

BASE_URL = "http://localhost:5050/api"

def run_tests():
    print("=== STARTING ANONYMOUS INTAKE INTEGRATION TESTS ===")

    # 1. Register a child anonymously
    print("\n[1] Registering child anonymously...")
    child_payload = {
        "name": "Anon Test Student",
        "age": 11,
        "language": "English",
        "school_year": "Class 5",
        "gender": "Girl",
        "exp_kinesthetic": 2,
        "exp_creative": 3,
        "exp_logical": 1
    }
    r = requests.post(f"{BASE_URL}/children", json=child_payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code == 201, "Failed to create child anonymously"
    child_data = r.json()
    child_id = child_data.get("id")
    assert child_id is not None, "Child ID is None"
    print(f"SUCCESS: Created child ID {child_id}")

    # 2. Create a session anonymously
    print("\n[2] Creating session anonymously...")
    session_payload = {
        "child_id": child_id
    }
    r = requests.post(f"{BASE_URL}/sessions", json=session_payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code == 201, "Failed to create session anonymously"
    session_data = r.json()
    session_id = session_data.get("id")
    assert session_id is not None, "Session ID is None"
    print(f"SUCCESS: Created session ID {session_id}")

    # 3. Submit discovery questionnaire anonymously
    print("\n[3] Submitting discovery anonymously...")
    discovery_payload = {
        "child_id": child_id,
        "answers": {
            "q_discovery_1": 1,
            "q_discovery_2": 2
        }
    }
    r = requests.post(f"{BASE_URL}/sessions/{session_id}/discovery", json=discovery_payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code == 200, "Failed to submit discovery anonymously"
    print("SUCCESS: Submitted discovery anonymously")

    # 4. Fetch the session anonymously
    print("\n[4] Fetching session anonymously...")
    r = requests.get(f"{BASE_URL}/sessions/{session_id}")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code == 200, "Failed to fetch session anonymously"
    session_info = r.json()
    assert session_info.get("organization_id") == 1, f"Expected org 1, got {session_info.get('organization_id')}"
    assert session_info.get("center_id") is None, f"Expected center None, got {session_info.get('center_id')}"
    print("SUCCESS: Session verified as Org 1 and Center None (unassigned)")

    # 5. Simulate facilitator login and claiming the child/session
    print("\n[5] Generating mock facilitator session in active database...")
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path=env_path)
    
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
                except Exception:
                    pass
            db_url = f"postgresql://postgres.{project_ref}:{password}@{pooler_host}:{pooler_port}/{dbname}"
            os.environ["DATABASE_URL"] = db_url

    is_postgres = db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://"))
    
    if is_postgres:
        import psycopg2
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        conn = psycopg2.connect(db_url)
        print("Connected to PostgreSQL database.")
    else:
        db_path = os.path.join(os.path.dirname(__file__), "db", "goat.db")
        conn = sqlite3.connect(db_path)
        print("Connected to SQLite database.")
        
    cur = conn.cursor()
    
    # Query facilitator (try deep@goat.com then facilitator@goat.com)
    target_email = 'deep@goat.com'
    if is_postgres:
        cur.execute("SELECT id FROM users WHERE email=%s", (target_email,))
    else:
        cur.execute("SELECT id FROM users WHERE email=?", (target_email,))
    user_row = cur.fetchone()
    
    if not user_row:
        target_email = 'facilitator@goat.com'
        if is_postgres:
            cur.execute("SELECT id FROM users WHERE email=%s", (target_email,))
        else:
            cur.execute("SELECT id FROM users WHERE email=?", (target_email,))
        user_row = cur.fetchone()
        
    if not user_row:
        print(f"Facilitator not found. Creating {target_email} dynamically...")
        if is_postgres:
            raise ValueError("No seeded facilitator found in PostgreSQL. Please seed deep@goat.com in auth.users first.")
        else:
            cur.execute("INSERT OR IGNORE INTO organizations (id, name) VALUES (1, 'GOAT Labs')")
            cur.execute("INSERT OR IGNORE INTO centers (id, name, location, organization_id) VALUES (1, 'New Delhi Center', 'Okhla, New Delhi', 1)")
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role, organization_id, center_id)
                VALUES ('Demo Facilitator', 'facilitator@goat.com', 'dummy_hash', 'facilitator', 1, 1)
            """)
            conn.commit()
            cur.execute("SELECT id FROM users WHERE email=?", ('facilitator@goat.com',))
            user_row = cur.fetchone()
            
    user_id = user_row[0]
    
    # Ensure they have center_id = 1 to test claiming
    print(f"Selected facilitator {target_email} (ID: {user_id}) for testing. Ensuring center_id = 1...")
    if is_postgres:
        cur.execute("UPDATE users SET center_id = 1 WHERE id = %s", (user_id,))
    else:
        cur.execute("UPDATE users SET center_id = 1 WHERE id = ?", (user_id,))
    conn.commit()
        
    user_id = user_row[0]
    test_token = "test_facilitator_auth_token_xyz123"
    
    if is_postgres:
        cur.execute("DELETE FROM auth_sessions WHERE user_id = %s OR token = %s", (user_id, test_token))
        cur.execute("""
            INSERT INTO auth_sessions (user_id, token, expires_at)
            VALUES (%s, %s, CURRENT_TIMESTAMP + INTERVAL '1 hour')
        """, (user_id, test_token))
    else:
        cur.execute("""
            INSERT OR REPLACE INTO auth_sessions (user_id, token, expires_at)
            VALUES (?, ?, datetime('now', '+1 hour'))
        """, (user_id, test_token))
        
    conn.commit()
    conn.close()
    
    headers = {"Authorization": f"Bearer {test_token}"}
    print("Mock session generated in active database successfully.")

    # Fetch the session as the facilitator (center_id = 1)
    print("\n[6] Fetching session as Facilitator (Center 1) to claim child...")
    r = requests.get(f"{BASE_URL}/sessions/{session_id}", headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    assert r.status_code == 200, "Facilitator forbidden from fetching session"
    session_info_claimed = r.json()
    
    # Confirm it has been auto-assigned to Center 1!
    assert session_info_claimed.get("center_id") == 1, f"Expected auto-assignment to center 1, got {session_info_claimed.get('center_id')}"
    print("SUCCESS: Session was automatically claimed and assigned to Center 1!")

    print("\n=============================================")
    print("ALL ANONYMOUS INTAKE & AUTO-CLAIM TESTS PASSED!")
    print("=============================================")

if __name__ == "__main__":
    run_tests()
