import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(dotenv_path=env_path)

supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

print("=== Supabase Synchronization Integration Test ===")
print("URL:", supabase_url)

if not supabase_url or not supabase_key:
    print("ERROR: Missing Supabase credentials in backend/.env")
    exit(1)

try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("SUCCESS: Supabase Client initialized.")
    
    # 1. Test Static Tables Seeding Check
    print("\n[1] Checking static tables...")
    centers = supabase.table("centers").select("id").limit(1).execute()
    mentors = supabase.table("mentors").select("id").limit(1).execute()
    print(f"Centers present: {len(centers.data) > 0}")
    print(f"Mentors present: {len(mentors.data) > 0}")
    
    if not centers.data:
        print("Seeding centers...")
        supabase.table("centers").insert([
            {"id": 1, "name": "New Delhi Center", "location": "Okhla, New Delhi"},
            {"id": 2, "name": "Mumbai Center", "location": "Dharavi, Mumbai"}
        ]).execute()
    if not mentors.data:
        print("Seeding mentors...")
        supabase.table("mentors").insert([
            {"id": 1, "name": "Anita Sharma", "domain": "creative", "contact": "anita@why.org"}
        ]).execute()

    # 2. Test inserting a test child
    print("\n[2] Testing child insert...")
    child_data = {
        "name": "Supabase Test Student",
        "age": 12,
        "language": "English",
        "school_year": "Grade 7",
        "gender": "Male"
    }
    res_child = supabase.table("children").insert(child_data).execute()
    assert res_child.data and len(res_child.data) > 0, "Failed to insert child"
    child_id = res_child.data[0]["id"]
    print(f"SUCCESS: Inserted child with ID: {child_id}")
    
    # 3. Test inserting a session
    print("\n[3] Testing session insert...")
    session_data = {
        "child_id": child_id,
        "phase": "discovery",
        "status": "in_progress"
    }
    res_session = supabase.table("sessions").insert(session_data).execute()
    assert res_session.data and len(res_session.data) > 0, "Failed to insert session"
    session_id = res_session.data[0]["id"]
    print(f"SUCCESS: Inserted session with ID: {session_id}")
    
    # 4. Test updating discovery
    print("\n[4] Testing session update (Discovery)...")
    disc_answers = {"q_discovery_1": 0, "q_discovery_2": 2}
    tasks = [{"key": "logical_pattern_matrix", "domain": "logical"}]
    update_discovery = {
        "responses": json.dumps(disc_answers),
        "generated_tasks": json.dumps(tasks),
        "phase": "assess"
    }
    res_update_disc = supabase.table("sessions").update(update_discovery).eq("id", session_id).execute()
    assert res_update_disc.data and len(res_update_disc.data) > 0, "Failed to update discovery"
    print("SUCCESS: Session updated to phase 'assess'")
    
    # 5. Test updating assessment results
    print("\n[5] Testing session update (Assessment results)...")
    update_results = {
        "responses": json.dumps({**disc_answers, "logical_pattern_matrix": {"value": 4, "domain": "logical"}}),
        "domain_flags": json.dumps(["logical"]),
        "tq_scores": json.dumps({"logical": 90}),
        "eq_score": 75,
        "visualizer_score": 80,
        "personality_data": json.dumps({"metrics": {}}),
        "integrated_score": json.dumps({"logical": 90}),
        "top_domain": "logical",
        "phase": "complete",
        "status": "complete"
    }
    res_update_res = supabase.table("sessions").update(update_results).eq("id", session_id).execute()
    assert res_update_res.data and len(res_update_res.data) > 0, "Failed to update results"
    print("SUCCESS: Session updated to status 'complete'")
    
    # 6. Test match and milestones insert
    print("\n[6] Testing match and milestone inserts...")
    match_data = {
        "child_id": child_id,
        "mentor_id": 1,
        "domain": "logical",
        "plan": json.dumps([{"title": "Intro Session", "done": False}])
    }
    res_match = supabase.table("mentor_matches").insert(match_data).execute()
    assert res_match.data and len(res_match.data) > 0, "Failed to insert match"
    match_id = res_match.data[0]["id"]
    print(f"SUCCESS: Inserted match with ID: {match_id}")
    
    milestone_data = {
        "match_id": match_id,
        "title": "Intro Session",
        "done": 0
    }
    res_milestone = supabase.table("milestones").insert(milestone_data).execute()
    assert res_milestone.data and len(res_milestone.data) > 0, "Failed to insert milestone"
    milestone_id = res_milestone.data[0]["id"]
    print(f"SUCCESS: Inserted milestone with ID: {milestone_id}")
    
    # 7. Test milestone update
    print("\n[7] Testing milestone update...")
    update_milestone = {
        "done": 1,
        "note": "Completed first introduction successfully."
    }
    res_up_m = supabase.table("milestones").update(update_milestone).eq("id", milestone_id).execute()
    assert res_up_m.data and len(res_up_m.data) > 0, "Failed to update milestone"
    print("SUCCESS: Milestone updated successfully.")
    
    # Clean up test data (in reverse order due to foreign keys)
    print("\n[8] Cleaning up test data from Supabase...")
    supabase.table("milestones").delete().eq("id", milestone_id).execute()
    supabase.table("mentor_matches").delete().eq("id", match_id).execute()
    supabase.table("sessions").delete().eq("id", session_id).execute()
    supabase.table("children").delete().eq("id", child_id).execute()
    print("SUCCESS: Clean up complete!")
    
    print("\n==========================================")
    print("ALL TESTS PASSED: Supabase integration works!")
    print("==========================================")
    
except Exception as e:
    print("\nERROR/EXCEPTION ENCOUNTERED:")
    import traceback
    traceback.print_exc()
    exit(1)
