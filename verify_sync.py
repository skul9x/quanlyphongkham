import time
import database
import supabase_config
from supabase import create_client

def test_sync():
    print("--- STARTING SYNC VERIFICATION ---")
    
    # 1. Initialize DB (starts sync manager)
    print("[1/3] Initializing Database & Sync Manager...")
    try:
        database.initialize_database()
    except Exception as e:
        print(f"Init Warning: {e}")

    # 2. Add patient to local DB
    test_name = f"Test Sync {int(time.time())}"
    print(f"[2/3] Adding local patient: '{test_name}'...")
    database.add_patient_db(test_name, "2024-01-01", "Nam", "Vietnam", "0900000000", "20kg", "Testing Auto-Sync")
    
    print("      Waiting 5 seconds for background sync...")
    time.sleep(5)
    
    # 3. Check Supabase directly
    print("[3/3] Checking Supabase for record...")
    try:
        url = supabase_config.SUPABASE_URL
        key = supabase_config.SUPABASE_KEY
        client = create_client(url, key)
        
        response = client.table("patients").select("*").eq("name", test_name).execute()
        
        if response.data and len(response.data) > 0:
            print("\n✅ VERIFICATION SUCCESSFUL!")
            print(f"   Found record in Supabase: ID={response.data[0]['id']}, Name={response.data[0]['name']}")
            print("   Auto-Sync is working correctly.")
        else:
            print("\n❌ VERIFICATION FAILED.")
            print("   Record not found in Supabase.")
            print("   Check sync_manager.py logs or internet connection.")
            
    except Exception as e:
        print(f"\n❌ ERROR CHECKING SUPABASE: {e}")

if __name__ == "__main__":
    test_sync()
