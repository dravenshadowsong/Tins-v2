import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(__file__))

from server import app, get_db, generate_ai_tasks, supabase_client

def test():
    if not supabase_client:
        print("Supabase client not initialized.")
        return
        
    print("Generating tasks...")
    with app.app_context():
        db = get_db()
        child = db.execute("SELECT * FROM children LIMIT 1").fetchone()
        if not child:
            print("No child found.")
            return
        child = dict(child)
        
        answers = {
            "q_discovery_1": 1,
            "q_discovery_2": 2
        }
        generated_tasks = generate_ai_tasks(child, answers)
        print(f"Generated {len(generated_tasks)} tasks.")
        
        update_data = {
            "responses": json.dumps(answers),
            "generated_tasks": json.dumps(generated_tasks),
            "phase": "assess"
        }
        
        try:
            print("Executing update with actual tasks payload...")
            res = supabase_client.table("sessions").update(update_data).eq("id", 38).execute()
            print("SUCCESS! Update executed successfully with full tasks payload!")
            print(f"Response data: {res.data}")
        except Exception as e:
            print("====== SUPABASE TASK UPDATE EXCEPTION ======")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            import traceback
            tb = traceback.format_exc()
            with open("debug_supabase_tasks_err.txt", "w", encoding="utf-8") as f:
                f.write(tb)
            print("Saved traceback to debug_supabase_tasks_err.txt")
            print("============================================")

if __name__ == "__main__":
    test()
