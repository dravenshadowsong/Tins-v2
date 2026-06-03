import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), "backend", ".env")
load_dotenv(dotenv_path=env_path)

supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

print("--- Supabase Client Auth Test ---")
print("Supabase URL:", supabase_url)
print("Supabase Key:", (supabase_key[:30] + "...") if supabase_key else "None")

if not supabase_url or not supabase_key:
    print("ERROR: Missing Supabase credentials in backend/.env")
    exit(1)

try:
    print("\n[1/2] Connecting and building Supabase client...")
    supabase: Client = create_client(supabase_url, supabase_key)
    print("Client initialized successfully.")
    
    print("\n[2/2] Attempting to query '_test' table...")
    try:
        response = supabase.table('_test').select('*').limit(1).execute()
        print("SUCCESS! Query on '_test' table completed.")
        print("Data:", response.data)
    except Exception as db_err:
        print(f"Query on '_test' failed: {db_err}")
        print("This is normal if '_test' table does not exist. Retrying with 'centers' table...")
        
        # Retry with centers table (which exists in our seed schema)
        response = supabase.table('centers').select('*').limit(1).execute()
        print("SUCCESS! Query on 'centers' table completed.")
        print("Data:", response.data)
        
except Exception as e:
    print("\nAUTHENTICATION/CONNECTION FAILED:")
    print(e)
