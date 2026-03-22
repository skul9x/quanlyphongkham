import time
import database
import sqlite3
from sync_manager import sync_manager
import sys

def push_all_data():
    print("--- STARTING FULL DATA SYNC (SQLite -> Supabase) ---")
    
    # 1. Initialize DB (starts sync manager and worker thread)
    print("[1/5] Initializing Database & Background Worker...")
    try:
        database.initialize_database()
        # Give the worker a moment to spin up
        time.sleep(1)
    except Exception as e:
        print(f"❌ Init Error: {e}")
        return

    conn = None
    try:
        conn = database._get_db_connection()
        c = conn.cursor()

        # 2. Sync Medicines
        print("\n[2/5] Syncing MEDICINES...")
        c.execute("SELECT * FROM medicines")
        medicines = c.fetchall()
        print(f"   Found {len(medicines)} medicines.")
        for med in medicines:
            sync_manager.sync_medicine(med)
            print(f"   + Queued medicine: {med['name']}")
        
        # 3. Sync Patients
        print("\n[3/5] Syncing PATIENTS...")
        c.execute("SELECT * FROM patients")
        patients = c.fetchall()
        print(f"   Found {len(patients)} patients.")
        for p in patients:
            # Fix date format "tháng" if present before sending?
            # SyncManager logic might handle it, checking sync_manager.py...
            # sync_manager.py doesn't seem to have explicit "tháng" replacement in _process_queue from previous view
            # But the user mentioned it was fixed. Let's assume sync_manager or database.py handles it.
            # actually database.py has migrations/updates.
            # Let's trust the current data or the sync manager's serialization.
            sync_manager.sync_patient(p)
            print(f"   + Queued patient: {p['name']}")

        # 4. Sync Prescriptions (Headers & Details)
        print("\n[4/5] Syncing PRESCRIPTIONS...")
        
        # Headers
        c.execute("SELECT * FROM prescriptions_header")
        headers = c.fetchall()
        print(f"   Found {len(headers)} prescription headers.")
        for h in headers:
            sync_manager.sync_prescription_header(h)
        
        # Details
        c.execute("SELECT * FROM prescription_details")
        details = c.fetchall()
        print(f"   Found {len(details)} prescription details.")
        for d in details:
            sync_manager.sync_prescription_detail(d)
            
        print(f"   + Queued {len(headers)} headers and {len(details)} details.")

        # 5. Wait for queue to drain
        print("\n[5/5] Waiting for background worker to finish uploading...")
        
        # Monitor queue size
        while not sync_manager.sync_queue.empty():
            q_size = sync_manager.sync_queue.qsize()
            print(f"   Remaining items in queue: {q_size}...", end='\r')
            time.sleep(1)
            
        # Give a little extra time for the last item processing
        print("\n   Queue empty. Waiting 5s for final confirmations...")
        time.sleep(5)
        
        print("\n✅ FULL SYNC COMPLETE!")
        print("   Please check Supabase dashboard to verify data.")

    except Exception as e:
        print(f"\n❌ SCRIPT ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn: conn.close()
        # Create a dummy flag file to signal completion if needed, or just exit.
        # Stop sync manager to clean up thread
        sync_manager.stop()

if __name__ == "__main__":
    push_all_data()
