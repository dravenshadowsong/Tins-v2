import os
import json
import sqlite3
from dotenv import load_dotenv
from supabase import create_client

env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(dotenv_path=env_path)

supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if supabase_key == "your-secret-service-role-key":
    supabase_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

print("Initializing Supabase Client...")
supabase = create_client(supabase_url, supabase_key)

db_path = os.path.join(os.path.dirname(__file__), "backend", "db", "goat.db")
print("Connecting to local SQLite database at:", db_path)
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 1. Sync Children
print("\n--- Syncing Children ---")
children = cursor.execute("SELECT * FROM children").fetchall()
for c in children:
    c_dict = dict(c)
    print(f"Child ID {c_dict['id']}: {c_dict['name']}")
    res = supabase.table("children").select("id").eq("id", c_dict["id"]).execute()
    if not res.data:
        print(f"  Pushing child {c_dict['name']} to Supabase...")
        supabase.table("children").insert(c_dict).execute()
    else:
        print("  Already in Supabase.")

# 2. Sync Sessions
print("\n--- Syncing Sessions ---")
sessions = cursor.execute("SELECT * FROM sessions").fetchall()
for s in sessions:
    s_dict = dict(s)
    print(f"Session ID {s_dict['id']} (Child ID: {s_dict['child_id']})")
    res = supabase.table("sessions").select("id").eq("id", s_dict["id"]).execute()
    if not res.data:
        print(f"  Pushing session {s_dict['id']} to Supabase...")
        supabase.table("sessions").insert(s_dict).execute()
    else:
        print("  Already in Supabase.")

# 3. Sync Mentor Matches
print("\n--- Syncing Mentor Matches ---")
matches = cursor.execute("SELECT * FROM mentor_matches").fetchall()
for m in matches:
    m_dict = dict(m)
    print(f"Match ID {m_dict['id']} (Child ID: {m_dict['child_id']}, Mentor ID: {m_dict['mentor_id']})")
    res = supabase.table("mentor_matches").select("id").eq("id", m_dict["id"]).execute()
    if not res.data:
        print(f"  Pushing match {m_dict['id']} to Supabase...")
        supabase.table("mentor_matches").insert(m_dict).execute()
    else:
        print("  Already in Supabase.")

# 4. Sync Milestones
print("\n--- Syncing Milestones ---")
milestones = cursor.execute("SELECT * FROM milestones").fetchall()
for mil in milestones:
    mil_dict = dict(mil)
    print(f"Milestone ID {mil_dict['id']} (Match ID: {mil_dict['match_id']}): {mil_dict['title']}")
    res = supabase.table("milestones").select("id").eq("id", mil_dict["id"]).execute()
    if not res.data:
        print(f"  Pushing milestone {mil_dict['id']} to Supabase...")
        supabase.table("milestones").insert(mil_dict).execute()
    else:
        print("  Already in Supabase.")

conn.close()
print("\nSync completed successfully!")
