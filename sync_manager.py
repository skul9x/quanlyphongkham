import threading
import queue
import time
import json
import traceback
import re
from datetime import datetime
from supabase import create_client, Client
import supabase_config
import config

class SyncManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SyncManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
            
        self.initialized = True
        self.client: Client = None
        self.sync_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        try:
            self.client = create_client(supabase_config.SUPABASE_URL, supabase_config.SUPABASE_KEY)
            print("[SYNC] Supabase client initialized")
        except Exception as e:
            print(f"[SYNC] Failed to initialize Supabase client: {e}")

    def start(self):
        """Start the background sync worker"""
        if not self.client:
            print("[SYNC] Client not ready, skipping start")
            return
            
        if self.is_running:
            return
            
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        print("[SYNC] Worker thread started")

    def stop(self):
        """Stop the background sync worker"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)

    def _process_queue(self):
        """Main worker loop to process sync tasks"""
        while self.is_running:
            try:
                # Get task with timeout to allow checking is_running
                try:
                    task = self.sync_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                table = task.get('table')
                action = task.get('action') # 'upsert' or 'delete'
                data = task.get('data')
                
                print(f"[SYNC] Processing {action} on {table}...")
                
                # [FIX] Simple Retry with exponential backoff
                max_retries = 3
                retry_delays = [1, 3, 5]  # seconds
                success = False
                
                for attempt in range(max_retries):
                    try:
                        if action == 'delete':
                            self.client.table(table).delete().eq('id', data['id']).execute()
                        else:
                            # Make a copy to avoid modifying original data
                            sync_data = dict(data)
                            
                            # [FIX] Filter out internal columns not in Supabase
                            if table == 'patients' and 'prescription_migrated' in sync_data:
                                del sync_data['prescription_migrated']
                            
                            # [FIX] v4.5.2: Validate DOB before sync
                            if table == 'patients':
                                sync_data = self._sanitize_patient_data(sync_data)
                                
                            # Ensure dates are serialized properly if needed
                            self.client.table(table).upsert(sync_data).execute()
                            
                        print(f"[SYNC] {action} on {table} SUCCESS")
                        success = True
                        break  # Exit retry loop on success
                        
                    except Exception as e:
                        if attempt < max_retries - 1:
                            delay = retry_delays[attempt]
                            print(f"[SYNC] Attempt {attempt + 1}/{max_retries} failed. Retrying in {delay}s... Error: {e}")
                            time.sleep(delay)
                        else:
                            print(f"[SYNC] FAILED after {max_retries} attempts: {action} on {table}")
                            print(f"[SYNC] Error: {e}")
                            traceback.print_exc()
                
                if not success:
                    print(f"[SYNC] ⚠️ Data may be out of sync for {table} id={data.get('id', 'unknown')}")
                    
                self.sync_queue.task_done()
                
            except Exception as e:
                print(f"[SYNC] Worker loop error: {e}")
                time.sleep(1)

    def _sanitize_patient_data(self, data: dict) -> dict:
        """
        Sanitize patient data before syncing to Supabase.
        Fixes common data issues like invalid date formats.
        """
        # Validate and fix DOB field
        dob = data.get('dob')
        if dob:
            # Check if DOB is a valid date format (YYYY-MM-DD or DD-MM-YYYY)
            valid_date = False
            
            # Pattern 1: YYYY-MM-DD
            if re.match(r'^\d{4}-\d{2}-\d{2}$', str(dob)):
                valid_date = True
            # Pattern 2: DD-MM-YYYY
            elif re.match(r'^\d{2}-\d{2}-\d{4}$', str(dob)):
                valid_date = True
            # Pattern 3: DD/MM/YYYY
            elif re.match(r'^\d{2}/\d{2}/\d{4}$', str(dob)):
                valid_date = True
            
            if not valid_date:
                # Invalid DOB like "18 tháng", "6 tuổi", "" -> set to None
                print(f"[SYNC] Sanitizing invalid DOB: '{dob}' -> None")
                data['dob'] = None
        
        # Handle empty string DOB
        if data.get('dob') == '':
            data['dob'] = None
            
        return data

    # --- Public API for Database Triggers ---

    def sync_patient(self, patient_data):
        """Queue a patient for sync (Insert/Update)"""
        # Convert sqlite3.Row or tuple to dict if needed
        data = dict(patient_data)
        self.sync_queue.put({
            'table': 'patients',
            'action': 'upsert',
            'data': data
        })

    def delete_patient(self, patient_id):
        """Queue a patient deletion (async, may not complete before app closes)"""
        self.sync_queue.put({
            'table': 'patients',
            'action': 'delete',
            'data': {'id': patient_id}
        })

    def delete_patient_sync(self, patient_id):
        """
        [v5.0.3] Synchronous delete - waits for Cloud deletion to complete.
        Use this instead of delete_patient() to ensure Mobile App doesn't see deleted data.
        
        Returns:
            True if Cloud delete succeeded, False otherwise
        """
        if not self.client:
            print(f"[SYNC] Client not ready, skipping cloud delete for patient {patient_id}")
            return False
        
        try:
            self.client.table('patients').delete().eq('id', patient_id).execute()
            print(f"[SYNC] Deleted patient {patient_id} from Cloud (sync)")
            return True
        except Exception as e:
            print(f"[SYNC] Cloud delete failed for patient {patient_id}: {e}")
            # Don't raise - local delete already succeeded, just log the error
            return False

    def sync_medicine(self, medicine_data):
        """Queue a medicine for sync"""
        data = dict(medicine_data)
        self.sync_queue.put({
            'table': 'medicines',
            'action': 'upsert',
            'data': data
        })
        
    def delete_medicine(self, medicine_id):
        self.sync_queue.put({
            'table': 'medicines',
            'action': 'delete',
            'data': {'id': medicine_id}
        })

    def sync_prescription_header(self, header_data):
        data = dict(header_data)
        self.sync_queue.put({
            'table': 'prescriptions_header',
            'action': 'upsert',
            'data': data
        })
        
    def sync_prescription_detail(self, detail_data):
        data = dict(detail_data)
        self.sync_queue.put({
            'table': 'prescription_details',
            'action': 'upsert',
            'data': data
        })

    # ==========================================================================
    # TWO-WAY SYNC: Cloud as Source of Truth (v4.5)
    # ==========================================================================

    def startup_sync(self, progress_callback=None):
        """
        Called on app startup to sync Local <-> Cloud.
        If local is empty, pulls everything from Cloud.
        Otherwise, performs incremental comparison.
        
        Args:
            progress_callback: Optional function(message, percent) to update UI
        """
        if not self.client:
            print("[SYNC] Client not ready, skipping startup sync")
            return False
            
        try:
            import database
            
            if progress_callback:
                progress_callback("Đang kiểm tra dữ liệu...", 10)
            
            # Check if local database is empty
            local_patient_count = database.get_total_patient_count()
            
            if local_patient_count == 0:
                # Local is empty - Full restore from Cloud
                print("[SYNC] Local database empty. Performing full restore from Cloud...")
                if progress_callback:
                    progress_callback("Database trống. Đang khôi phục từ Cloud...", 20)
                return self.pull_all_from_cloud(progress_callback)
            else:
                # Incremental sync
                print(f"[SYNC] Local has {local_patient_count} patients. Checking for Cloud updates...")
                if progress_callback:
                    progress_callback("Đang kiểm tra cập nhật từ Cloud...", 20)
                return self._incremental_sync(progress_callback)
                
        except Exception as e:
            print(f"[SYNC] Startup sync error: {e}")
            traceback.print_exc()
            return False

    def pull_all_from_cloud(self, progress_callback=None):
        """
        Pull ALL data from Supabase Cloud to local SQLite.
        Used when local database is empty (fresh install or data loss).
        """
        if not self.client:
            return False
            
        try:
            import database
            
            # 1. Pull Medicines first (referenced by prescriptions)
            if progress_callback:
                progress_callback("Đang tải danh sách thuốc...", 30)
            
            response = self.client.table('medicines').select('*').execute()
            medicines = response.data or []
            print(f"[SYNC] Pulling {len(medicines)} medicines from Cloud...")
            
            for med in medicines:
                database.insert_medicine_from_cloud(med)
            
            # 2. Pull Patients
            if progress_callback:
                progress_callback("Đang tải danh sách bệnh nhân...", 50)
            
            response = self.client.table('patients').select('*').execute()
            patients = response.data or []
            print(f"[SYNC] Pulling {len(patients)} patients from Cloud...")
            
            for p in patients:
                database.insert_patient_from_cloud(p)
            
            # 3. Pull Prescription Headers
            if progress_callback:
                progress_callback("Đang tải đơn thuốc...", 70)
            
            response = self.client.table('prescriptions_header').select('*').execute()
            headers = response.data or []
            print(f"[SYNC] Pulling {len(headers)} prescription headers from Cloud...")
            
            for h in headers:
                database.insert_prescription_header_from_cloud(h)
            
            # 4. Pull Prescription Details
            if progress_callback:
                progress_callback("Đang tải chi tiết đơn thuốc...", 85)
            
            response = self.client.table('prescription_details').select('*').execute()
            details = response.data or []
            print(f"[SYNC] Pulling {len(details)} prescription details from Cloud...")
            
            for d in details:
                database.insert_prescription_detail_from_cloud(d)
            
            # [FIX] v4.5.1: Run migration to convert legacy medical_history to new format
            # This is needed because Cloud stores data in legacy format (medical_history column)
            # but Desktop v4.4 reads from prescriptions_header/prescription_details tables
            if progress_callback:
                progress_callback("Đang chuyển đổi dữ liệu...", 95)
            
            database._migrate_legacy_prescriptions()
            
            # [FIX] v5.0.2: Reset AUTOINCREMENT sequences to prevent ID conflicts
            self._reset_autoincrement_sequences()
            
            if progress_callback:
                progress_callback("Hoàn tất khôi phục!", 100)
            
            print(f"[SYNC] Full restore complete: {len(medicines)} medicines, {len(patients)} patients, {len(headers)} prescriptions")
            return True
            
        except Exception as e:
            print(f"[SYNC] Pull from cloud error: {e}")
            traceback.print_exc()
            return False

    def _reset_autoincrement_sequences(self):
        """
        [v5.0.2] Reset SQLite AUTOINCREMENT sequences after cloud restore.
        Prevents ID conflicts when creating new records after restoring old data.
        """
        try:
            import database
            conn = database._get_db_connection()
            c = conn.cursor()
            
            tables = ['patients', 'medicines', 'prescriptions_header', 'prescription_details']
            for table in tables:
                # Update sequence to max ID in table (or skip if table empty)
                c.execute(f"SELECT MAX(id) FROM {table}")
                max_id = c.fetchone()[0]
                if max_id:
                    c.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = ?", (max_id, table))
            
            conn.commit()
            conn.close()
            print("[SYNC] Reset AUTOINCREMENT sequences after restore")
        except Exception as e:
            print(f"[SYNC] Warning: Could not reset sequences: {e}")

    def _incremental_sync(self, progress_callback=None):
        """
        [v5.0.2] One-way Push Sync: Local is Master.
        - Records in Local but not in Cloud -> Push
        - Auto-pull DISABLED to prevent 'Zombie Data' resurrection.
        
        When user deletes a patient locally, we don't want Cloud to resurrect it
        on next startup. Full restore only happens via pull_all_from_cloud()
        when Local DB is empty (fresh install).
        """
        if not self.client:
            return False
            
        try:
            import database
            
            # Get Cloud IDs for patients
            if progress_callback:
                progress_callback("Đang so sánh dữ liệu...", 40)
            
            cloud_response = self.client.table('patients').select('id').execute()
            cloud_ids = set(r['id'] for r in (cloud_response.data or []))
            
            local_ids = set(database.get_all_patient_ids())
            
            # [v5.0.2] DISABLED auto-pull to prevent "Zombie Data" resurrection
            # If user deletes a patient locally, Cloud should NOT resurrect it.
            # Restore is only allowed via pull_all_from_cloud() when Local DB is empty.
            # 
            # COMMENTED OUT:
            # to_pull = cloud_ids - local_ids
            # if to_pull:
            #     for pid in to_pull:
            #         response = self.client.table('patients').select('*').eq('id', pid).execute()
            #         if response.data:
            #             database.insert_patient_from_cloud(response.data[0])
            
            # Records in Local but not Cloud -> Push (KEEP THIS)
            to_push = local_ids - cloud_ids
            if to_push:
                print(f"[SYNC] Found {len(to_push)} patients in Local not in Cloud. Pushing...")
                if progress_callback:
                    progress_callback(f"Đang đẩy {len(to_push)} bệnh nhân lên Cloud...", 60)
                
                for pid in to_push:
                    patient = database.get_patient_by_id(pid)
                    if patient:
                        self.sync_patient(patient)
            
            if progress_callback:
                progress_callback("Đồng bộ hoàn tất!", 100)
            
            print(f"[SYNC] Incremental sync complete. Pushed: {len(to_push)} (auto-pull disabled)")
            return True
            
        except Exception as e:
            print(f"[SYNC] Incremental sync error: {e}")
            traceback.print_exc()
            return False

# Singleton instance
sync_manager = SyncManager()

