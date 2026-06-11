import os
import sys
import json

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(__file__))

from server import app, get_db, generate_ai_tasks

def test():
    print("Running task generation diagnostic...")
    with app.app_context():
        db = get_db()
        child = db.execute("SELECT * FROM children LIMIT 1").fetchone()
        if not child:
            print("No child found. Creating a dummy child...")
            db.execute("INSERT INTO children (name, age, language) VALUES ('Test Child', 10, 'English')")
            db.commit()
            child = db.execute("SELECT * FROM children LIMIT 1").fetchone()
            
        child = dict(child)
        print(f"Testing with child: {child}")
        
        answers = {
            "q_discovery_1": 1,
            "q_discovery_2": 2
        }
        
        try:
            print("Calling generate_ai_tasks...")
            tasks = generate_ai_tasks(child, answers)
            print(f"Generated {len(tasks)} tasks.")
            
            print("Attempting to dump tasks to JSON...")
            dumped = json.dumps(tasks)
            print("Successfully dumped tasks to JSON!")
            print(f"JSON length: {len(dumped)}")
            
        except Exception as e:
            print("====== DIAGNOSTIC EXCEPTION ======")
            import traceback
            traceback.print_exc()
            print("==================================")

if __name__ == "__main__":
    test()
