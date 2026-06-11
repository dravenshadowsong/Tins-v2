import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(__file__))

from server import supabase_client

def test():
    if not supabase_client:
        print("Supabase client not initialized.")
        return
        
    print("Testing Supabase sessions update...")
    update_data = {
        "responses": json.dumps({"q_discovery_1": 1}),
        "generated_tasks": json.dumps([]),
        "phase": "assess"
    }
    
    try:
        # Let's try to update session 38 or a dummy session
        print("Executing update on sessions table...")
        res = supabase_client.table("sessions").update(update_data).eq("id", 38).execute()
        print("Update executed successfully!")
        print(f"Response data: {res.data}")
    except Exception as e:
        print("====== SUPABASE UPDATE EXCEPTION ======")
        print(f"Exception type: {type(e)}")
        print(f"Exception message: {str(e)}")
        import traceback
        tb = traceback.format_exc()
        print("Traceback (saved to debug_supabase_err.txt)")
        with open("debug_supabase_err.txt", "w", encoding="utf-8") as f:
            f.write(tb)
        print("=======================================")

if __name__ == "__main__":
    test()
