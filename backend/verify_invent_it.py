"""
Run Invent It schema migration via Supabase REST API (service role).
This works around network restrictions that prevent direct PostgreSQL connections.
"""
import os, sys, json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://ubsjcfaokemckctswnzi.supabase.co"
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SERVICE_KEY:
    print("[ERROR] SUPABASE_SERVICE_ROLE_KEY not set")
    sys.exit(1)

try:
    from supabase import create_client
    sb = create_client(SUPABASE_URL, SERVICE_KEY)
    print("[OK] Supabase client initialized.")
except Exception as e:
    print(f"[ERROR] Supabase client: {e}")
    sys.exit(1)

# Test tables existence by trying to select from them
tables = [
    "invent_it_sessions",
    "invent_it_responses",
    "invent_it_events",
    "invent_it_ai_analysis",
    "invent_it_behaviour_evidence",
    "invent_it_facilitator_obs",
]

print("\nChecking table existence via Supabase REST API...")
missing = []
for tbl in tables:
    try:
        r = sb.table(tbl).select("id").limit(1).execute()
        print(f"  ✓ {tbl} — exists ({len(r.data)} rows sampled)")
    except Exception as e:
        err = str(e)
        if "relation" in err and "does not exist" in err:
            print(f"  ✗ {tbl} — MISSING")
            missing.append(tbl)
        else:
            print(f"  ? {tbl} — Error: {err[:80]}")

if not missing:
    print("\n[SUCCESS] All Invent It tables exist in Supabase!")
else:
    print(f"\n[WARNING] Missing tables: {missing}")
    print("These will be created via the backend's _invent_it_init_sqlite() when the server starts.")
    print("For Supabase/PostgreSQL, please run the SQL in migrate_invent_it.py manually via the Supabase SQL Editor.")
    print("\nSQL Editor URL: https://supabase.com/dashboard/project/ubsjcfaokemckctswnzi/sql/new")

# Test a sample insert to verify RLS
print("\nTesting sample session insert...")
try:
    import uuid
    test_uuid = f"test-{uuid.uuid4().hex[:8]}"
    r = sb.table("invent_it_sessions").insert({
        "session_uuid": test_uuid,
        "language": "en",
        "status": "test",
        "experience_id": "invent_it_v1",
    }).execute()
    if r.data:
        print(f"  ✓ Insert OK — id={r.data[0].get('id')}")
        # Clean up test row
        sb.table("invent_it_sessions").delete().eq("session_uuid", test_uuid).execute()
        print(f"  ✓ Cleanup OK")
    else:
        print(f"  ? Insert returned no data")
except Exception as e:
    print(f"  ✗ Insert failed: {e}")

print("\nDone.")
