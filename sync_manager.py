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
                
                try:
                    if action == 'delete':
                        self.client.table(table).delete().eq('id', data['id']).execute()
                    else:
                        # [FIX] Filter out internal columns not in Supabase
                        if table == 'patients' and 'prescription_migrated' in data:
                            del data['prescription_migrated']
                        
                        # [FIX] v4.5.2: Validate DOB before sync
                        if table == 'patients':
                            data = self._sanitize_patient_data(data)
                            
                        # Ensure dates are serialized properly if needed
                        self.client.table(table).upsert(data).execute()
                        
                    print(f"[SYNC] {action} on {table} SUCCESS")
                    
                except Exception as e:
                    print(f"[SYNC] Error syncing to Supabase: {e}")
                    # Simple retry logic: put back in queue? 
                    # For now just log to avoid infinite loops on bad data
                    traceback.print_exc()
                    
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
        """Queue a patient deletion"""
        self.sync_queue.put({
            'table': 'patients',
            'action': 'delete',
            'data': {'id': patient_id}
        })

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
            
            if progress_callback:
                progress_callback("Hoàn tất khôi phục!", 100)
            
            print(f"[SYNC] Full restore complete: {len(medicines)} medicines, {len(patients)} patients, {len(headers)} prescriptions")
            return True
            
        except Exception as e:
            print(f"[SYNC] Pull from cloud error: {e}")
            traceback.print_exc()
            return False

    def _incremental_sync(self, progress_callback=None):
        """
        Compare local vs cloud and sync differences.
        - Records in Cloud but not in Local -> Pull
        - Records in Local but not in Cloud -> Push
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
            
            # Records in Cloud but not Local -> Pull
            to_pull = cloud_ids - local_ids
            if to_pull:
                print(f"[SYNC] Found {len(to_pull)} patients in Cloud not in Local. Pulling...")
                if progress_callback:
                    progress_callback(f"Đang tải {len(to_pull)} bệnh nhân mới...", 60)
                
                for pid in to_pull:
                    response = self.client.table('patients').select('*').eq('id', pid).execute()
                    if response.data:
                        database.insert_patient_from_cloud(response.data[0])
            
            # Records in Local but not Cloud -> Push
            to_push = local_ids - cloud_ids
            if to_push:
                print(f"[SYNC] Found {len(to_push)} patients in Local not in Cloud. Pushing...")
                if progress_callback:
                    progress_callback(f"Đang đẩy {len(to_push)} bệnh nhân lên Cloud...", 80)
                
                for pid in to_push:
                    patient = database.get_patient_by_id(pid)
                    if patient:
                        self.sync_patient(patient)
            
            if progress_callback:
                progress_callback("Đồng bộ hoàn tất!", 100)
            
            print(f"[SYNC] Incremental sync complete. Pulled: {len(to_pull)}, Pushed: {len(to_push)}")
            return True
            
        except Exception as e:
            print(f"[SYNC] Incremental sync error: {e}")
            traceback.print_exc()
            return False

# Singleton instance
sync_manager = SyncManager()

