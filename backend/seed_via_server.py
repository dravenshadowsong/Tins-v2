import os
import sys
import json

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(__file__))

from server import app, get_db, PostgresConnectionWrapper

def seed():
    bank_path = os.path.join(os.path.dirname(__file__), "db", "question_bank", "extended_bank.json")
    if not os.path.exists(bank_path):
        print(f"[ERROR] question bank file not found at {bank_path}")
        return

    with open(bank_path, "r", encoding="utf-8") as f:
        puzzles = json.load(f)
        
    print(f"Loaded {len(puzzles)} puzzles. Seeding via server.py context...")
    
    with app.app_context():
        db = get_db()
        
        # Check connection type
        is_postgres = isinstance(db, PostgresConnectionWrapper)
        print(f"Connected to database type: {'Postgres/Supabase' if is_postgres else 'SQLite'}")
        
        # Clear existing puzzles
        print("Clearing existing puzzles...")
        db.execute("DELETE FROM puzzles")
        
        # Insert all
        print("Inserting puzzles...")
        for p in puzzles:
            if is_postgres:
                db.execute("""
                    INSERT INTO puzzles (key, type, domain, component, data)
                    VALUES (%s, %s, %s, %s, %s)
                """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
            else:
                db.execute("""
                    INSERT OR REPLACE INTO puzzles (key, type, domain, component, data)
                    VALUES (?, ?, ?, ?, ?)
                """, (p["key"], p["type"], p["domain"], p.get("component", ""), json.dumps(p)))
        
        db.commit()
        print("[SUCCESS] Database seeding completed successfully via server context!")

if __name__ == "__main__":
    seed()
