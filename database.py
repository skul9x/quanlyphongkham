import sqlite3
from datetime import datetime
import pytz
import re
import config
import utils
import traceback
from sync_manager import sync_manager

# --- Connection ---
def _get_db_connection():
    try:
        # Increased timeout to 30s to handle potential locks
        conn = sqlite3.connect(config.get_database_path(), timeout=30)
        conn.create_function("remove_diacritics", 1, utils.remove_diacritics)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"[DB ERROR] Connection failed: {e}")
        traceback.print_exc()
        raise e

def initialize_database():
    print("[DB] Initializing database...")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob DATE,
                gender TEXT,
                address TEXT,
                phone TEXT,
                weight TEXT,
                medical_history TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                name_normalized TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions_image (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                image_path TEXT,
                prescription_date DATE,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS medicines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                packing_spec TEXT,
                price REAL DEFAULT 0.0
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prescriptions_header (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                prescription_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                diagnosis TEXT,
                total_amount REAL DEFAULT 0.0,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS prescription_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prescription_header_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                unit_price REAL,
                FOREIGN KEY (prescription_header_id) REFERENCES prescriptions_header(id) ON DELETE CASCADE,
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        ''')
        
        # --- Migration: Add name_normalized column if not exists ---
        c.execute("PRAGMA table_info(patients)")
        columns = [col[1] for col in c.fetchall()]
        if 'name_normalized' not in columns:
            print("[DB] Migrating: Adding name_normalized column...")
            c.execute("ALTER TABLE patients ADD COLUMN name_normalized TEXT")
        
        # --- Create indexes for search optimization ---
        c.execute("CREATE INDEX IF NOT EXISTS idx_patients_name_normalized ON patients(name_normalized)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_patients_created_at ON patients(created_at)")
        
        # --- Backfill name_normalized for existing records ---
        c.execute("SELECT id, name FROM patients WHERE name_normalized IS NULL AND name IS NOT NULL")
        rows_to_update = c.fetchall()
        if rows_to_update:
            print(f"[DB] Backfilling name_normalized for {len(rows_to_update)} records...")
            for row in rows_to_update:
                normalized = utils.remove_diacritics(row['name'].lower())
                c.execute("UPDATE patients SET name_normalized = ? WHERE id = ?", (normalized, row['id']))
            print("[DB] Backfill complete.")
        
        # --- Migration: Rename 'allergies' column to 'weight' ---
        if 'allergies' in columns and 'weight' not in columns:
            print("[DB] Migrating: Renaming 'allergies' column to 'weight'...")
            # SQLite doesn't support ALTER COLUMN RENAME directly in older versions
            # We need to recreate the table
            c.execute('''CREATE TABLE patients_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob DATE,
                gender TEXT,
                address TEXT,
                phone TEXT,
                weight TEXT,
                medical_history TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                name_normalized TEXT
            )''')
            c.execute('''INSERT INTO patients_new (id, name, dob, gender, address, phone, weight, medical_history, created_at, name_normalized)
                         SELECT id, name, dob, gender, address, phone, allergies, medical_history, created_at, name_normalized FROM patients''')
            c.execute('DROP TABLE patients')
            c.execute('ALTER TABLE patients_new RENAME TO patients')
            # Recreate indexes after table recreation
            c.execute("CREATE INDEX IF NOT EXISTS idx_patients_name_normalized ON patients(name_normalized)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_patients_created_at ON patients(created_at)")
            print("[DB] Migration complete: 'allergies' -> 'weight'.")
        
        # --- [v5.2.0] Add Prescription Indexes ---
        c.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_header_patient_id ON prescriptions_header(patient_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_prescriptions_header_date ON prescriptions_header(prescription_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_prescription_details_header_id ON prescription_details(prescription_header_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_prescription_details_medicine_id ON prescription_details(medicine_id)")
        
        # --- Migration: Add diagnosis and prescription_migrated columns to patients ---
        c.execute("PRAGMA table_info(patients)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'diagnosis' not in columns:
            print("[DB] Migrating: Adding diagnosis column to patients...")
            c.execute("ALTER TABLE patients ADD COLUMN diagnosis TEXT")
        
        if 'prescription_migrated' not in columns:
            print("[DB] Migrating: Adding prescription_migrated flag...")
            c.execute("ALTER TABLE patients ADD COLUMN prescription_migrated INTEGER DEFAULT 0")
        
        # --- Migration: Add diagnosis column to prescriptions_header if not exists ---
        c.execute("PRAGMA table_info(prescriptions_header)")
        ph_columns = [col[1] for col in c.fetchall()]
        if 'diagnosis' not in ph_columns:
            print("[DB] Migrating: Adding diagnosis column to prescriptions_header...")
            c.execute("ALTER TABLE prescriptions_header ADD COLUMN diagnosis TEXT")
        
        # --- Migration v5.1.0: Add stock columns to medicines ---
        c.execute("PRAGMA table_info(medicines)")
        med_columns = [col[1] for col in c.fetchall()]
        
        if 'stock_quantity' not in med_columns:
            print("[DB] Migrating: Adding stock_quantity column to medicines...")
            c.execute("ALTER TABLE medicines ADD COLUMN stock_quantity INTEGER DEFAULT 0")
        
        if 'min_stock_level' not in med_columns:
            print("[DB] Migrating: Adding min_stock_level column to medicines...")
            c.execute("ALTER TABLE medicines ADD COLUMN min_stock_level INTEGER DEFAULT 5")
        
        conn.commit()
        
        # --- Migration: Parse legacy medical_history and migrate to prescriptions ---
        _migrate_legacy_prescriptions()
        
        conn.commit()
        print("[DB] Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"[DB INIT ERROR] {e}")
        traceback.print_exc()
    finally:
        if conn: conn.close()
    
    # Start sync manager
    sync_manager.start()

# --- Patients ---
def add_patient_db(name, dob, gender, address, phone, weight, diagnosis):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        # Compute normalized name for indexed search
        name_normalized = utils.remove_diacritics(name.lower()) if name else None
        c.execute('''INSERT INTO patients
                     (name, dob, gender, address, phone, weight, medical_history, name_normalized)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (name, dob, gender, address, phone, weight, diagnosis, name_normalized))
        
        new_id = c.lastrowid
        c.execute("SELECT * FROM patients WHERE id=?", (new_id,))
        new_patient = c.fetchone()
        
        conn.commit()
        
        # [SYNC] Only sync AFTER commit succeeds (Fix Race Condition)
        if new_patient:
            sync_manager.sync_patient(new_patient)
        
        return new_id
    except sqlite3.Error as e:
        print(f"[DB ERROR] Add Patient: {e}")
        return None
    finally:
        if conn: conn.close()

def update_patient_db(patient_id, name, dob, gender, address, phone, weight, diagnosis):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        # Compute normalized name for indexed search
        name_normalized = utils.remove_diacritics(name.lower()) if name else None
        c.execute('''UPDATE patients
                     SET name=?, dob=?, gender=?, address=?, phone=?, weight=?, medical_history=?, name_normalized=?
                     WHERE id=?''',
                  (name, dob, gender, address, phone, weight, diagnosis, name_normalized, patient_id))
        c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        updated_patient = c.fetchone()

        conn.commit()
        
        # [SYNC] Only sync AFTER commit succeeds (Fix Race Condition)
        if updated_patient:
            sync_manager.sync_patient(updated_patient)
        
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn: conn.close()

def update_patient_with_timestamp_db(patient_id, name, dob, gender, address, phone, weight, diagnosis, new_utc_datetime_str):
    """
    Atomic update: Updates patient info AND created_at timestamp in a single transaction.
    Fixes Transaction Propagation Error where two separate updates could leave data inconsistent.
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        name_normalized = utils.remove_diacritics(name.lower()) if name else None
        c.execute('''UPDATE patients
                     SET name=?, dob=?, gender=?, address=?, phone=?, weight=?, medical_history=?, name_normalized=?, created_at=?
                     WHERE id=?''',
                  (name, dob, gender, address, phone, weight, diagnosis, name_normalized, new_utc_datetime_str, patient_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] update_patient_with_timestamp_db: {e}")
        return False
    finally:
        if conn: conn.close()

def update_visit_details_db(visit_id, weight, diagnosis):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # We need to preserve any existing medicines in medical_history 
        # (the part after the first newline) while only updating the diagnosis part.
        c.execute("SELECT medical_history FROM patients WHERE id=?", (visit_id,))
        row = c.fetchone()
        existing_history = row['medical_history'] if row and row['medical_history'] else ""
        
        parts = existing_history.split('\n', 1)
        existing_medicines = parts[1] if len(parts) > 1 else ""
        
        new_medical_history = diagnosis + ("\n" + existing_medicines if existing_medicines else "")
        
        # Update patients table
        c.execute('UPDATE patients SET weight=?, medical_history=?, diagnosis=? WHERE id=?', (weight, new_medical_history, diagnosis, visit_id))
        conn.commit()
        
        c.execute("SELECT * FROM patients WHERE id=?", (visit_id,))
        patient = c.fetchone()
        if patient:
            sync_manager.sync_patient(patient)
            
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] update_visit_details_db: {e}")
        traceback.print_exc()
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()


def update_patient_diagnosis_db(patient_id, new_diagnosis):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE patients SET medical_history = ? WHERE id = ?', (new_diagnosis, patient_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn: conn.close()

def update_patient_created_at_db(patient_id, new_utc_datetime_str):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE patients SET created_at=? WHERE id=?", (new_utc_datetime_str, patient_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn: conn.close()

def delete_visit_db(visit_id):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM patients WHERE id=?", (visit_id,))
        conn.commit()
        # [SYNC] v5.0.3: Use sync delete to ensure Cloud is updated immediately
        sync_manager.delete_patient_sync(visit_id)
        return True
    except sqlite3.Error:
        return False
    finally:
        if conn: conn.close()

def delete_patient_and_all_visits_db(name, dob):
    conn = None
    try:
        if not name:
            return False
            
        conn = _get_db_connection()
        c = conn.cursor()
        # [SYNC] Fetch IDs first to delete from Supabase
        c.execute("SELECT id FROM patients WHERE LOWER(name) = LOWER(?) AND (dob IS NULL OR dob = '')", (name.strip(),))
        ids_to_delete = [row['id'] for row in c.fetchall()]
        
        if dob:
            c.execute("DELETE FROM patients WHERE LOWER(name) = LOWER(?) AND dob = ?", (name.strip(), dob))
        else:
            c.execute("DELETE FROM patients WHERE LOWER(name) = LOWER(?) AND (dob IS NULL OR dob = '')", (name.strip(),))
        
        conn.commit()
        
        # [SYNC] v5.0.3: Use sync delete to ensure Cloud is updated immediately
        for pid in ids_to_delete:
            sync_manager.delete_patient_sync(pid)

        return True
    except sqlite3.Error:
        return False
    finally:
        if conn: conn.close()

def get_patient_by_id(patient_id):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        return c.fetchone()
    except sqlite3.Error:
        return None
    finally:
        if conn: conn.close()

def get_patients_paginated(page=1, page_size=50):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        offset = (page - 1) * page_size
        c.execute('''
            SELECT id, created_at, name, dob, gender, phone, address, weight, medical_history
            FROM patients
            ORDER BY datetime(created_at) DESC
            LIMIT ? OFFSET ?
        ''', (page_size, offset))
        return c.fetchall()
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_total_patient_count():
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM patients')
        res = c.fetchone()
        return res[0] if res else 0
    except sqlite3.Error:
        return 0
    finally:
        if conn: conn.close()

def search_patients_db(search_term, limit=None, offset=0):
    """
    Search patients by name or phone.
    Uses indexed name_normalized column for O(log N) performance instead of Full Table Scan.
    
    Args:
        search_term: Text to search for in name or phone
        limit: Maximum number of results to return (None = all)
        offset: Number of results to skip (for pagination)
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        # Normalize search term to match indexed column
        norm = utils.remove_diacritics(search_term.lower()) if search_term else ""
        
        query = '''
            SELECT id, created_at, name, dob, gender, phone, address, weight, medical_history
            FROM patients
            WHERE name_normalized LIKE ? OR phone LIKE ?
            ORDER BY datetime(created_at) DESC
        '''
        
        if limit is not None:
            query += f' LIMIT {int(limit)} OFFSET {int(offset)}'
        
        c.execute(query, (f'%{norm}%', f'%{search_term}%'))
        return c.fetchall()
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_all_diagnoses_by_name_dob(name, dob_iso):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        query = "SELECT medical_history FROM patients WHERE LOWER(name) = LOWER(?)"
        params = [name.strip()]
        
        if dob_iso:
            query += " AND dob = ?"
            params.append(dob_iso)
        else:
            query += " AND (dob IS NULL OR dob = '')"
            
        c.execute(query, tuple(params))
        return [row['medical_history'] for row in c.fetchall() if row['medical_history']]
    except sqlite3.Error as e:
        print(f"History Fetch Error: {e}")
        return []
    finally:
        if conn: conn.close()

# --- Medicines ---
def get_all_medicines_db():
    print("[DB] get_all_medicines_db called")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, packing_spec, price, stock_quantity, min_stock_level FROM medicines ORDER BY name COLLATE NOCASE")
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_all_medicines_db: {e}")
        return []
    finally:
        if conn: conn.close()

def add_medicine_db(name, spec, price, stock_quantity=0, min_stock_level=5):
    print(f"[DB] add_medicine_db called: {name}, {spec}, {price}, stock={stock_quantity}, min={min_stock_level}")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO medicines (name, packing_spec, price, stock_quantity, min_stock_level) VALUES (?, ?, ?, ?, ?)",
                  (name, spec, price, stock_quantity, min_stock_level))
        new_id = c.lastrowid
        
        c.execute("SELECT * FROM medicines WHERE id=?", (new_id,))
        new_med = c.fetchone()
        
        conn.commit()
        
        # [SYNC] Only sync AFTER commit succeeds (Fix Race Condition)
        if new_med:
            sync_manager.sync_medicine(new_med)
        
        print("[DB] Medicine added successfully, ID:", new_id)
        return new_id
    except sqlite3.Error as e:
        print(f"[DB ERROR] add_medicine_db: {e}")
        return None
    finally:
        if conn: conn.close()

def update_medicine_db(mid, name, spec, price, stock_quantity=None, min_stock_level=None):
    print(f"[DB] update_medicine_db called: ID={mid}, {name}, {spec}, {price}, stock={stock_quantity}, min={min_stock_level}")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        if stock_quantity is not None and min_stock_level is not None:
            c.execute("UPDATE medicines SET name=?, packing_spec=?, price=?, stock_quantity=?, min_stock_level=? WHERE id=?",
                      (name, spec, price, stock_quantity, min_stock_level, mid))
        else:
            c.execute("UPDATE medicines SET name=?, packing_spec=?, price=? WHERE id=?", (name, spec, price, mid))
        
        c.execute("SELECT * FROM medicines WHERE id=?", (mid,))
        updated_med = c.fetchone()

        conn.commit()
        
        # [SYNC] Only sync AFTER commit succeeds (Fix Race Condition)
        if updated_med:
            sync_manager.sync_medicine(updated_med)
        
        print("[DB] Medicine updated successfully")
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] update_medicine_db: {e}")
        return False
    finally:
        if conn: conn.close()

def delete_medicine_db(mid):
    print(f"[DB] delete_medicine_db called: ID={mid}")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        if is_medicine_in_use(mid): 
            print("[DB] Medicine is in use, cannot delete")
            return False
        c.execute("DELETE FROM medicines WHERE id=?", (mid,))
        conn.commit()
        
        # [SYNC]
        sync_manager.delete_medicine(mid)
        
        print("[DB] Medicine deleted successfully")
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] delete_medicine_db: {e}")
        return False
    finally:
        if conn: conn.close()

def get_medicine_by_id_db(mid):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, packing_spec, price, stock_quantity, min_stock_level FROM medicines WHERE id=?", (mid,))
        return c.fetchone()
    except sqlite3.Error:
        return None
    finally:
        if conn: conn.close()

def get_medicine_by_name_db(name):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id, name, packing_spec, price, stock_quantity, min_stock_level FROM medicines WHERE LOWER(name) = LOWER(?)", (name.strip(),))
        return c.fetchone()
    except sqlite3.Error:
        return None
    finally:
        if conn: conn.close()

def is_medicine_in_use(mid):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT 1 FROM prescription_details WHERE medicine_id = ? LIMIT 1", (mid,))
        return c.fetchone() is not None
    except sqlite3.Error:
        return True
    finally:
        if conn: conn.close()


# --- Inventory Management (v5.1.0) ---

def update_medicine_stock_db(medicine_id, new_quantity):
    """Update stock quantity for a medicine directly (manual stock adjustment)."""
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE medicines SET stock_quantity = ? WHERE id = ?", (new_quantity, medicine_id))
        
        c.execute("SELECT * FROM medicines WHERE id=?", (medicine_id,))
        updated_med = c.fetchone()
        
        conn.commit()
        
        if updated_med:
            sync_manager.sync_medicine(updated_med)
        
        print(f"[DB] Updated stock for medicine {medicine_id} to {new_quantity}")
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] update_medicine_stock_db: {e}")
        return False
    finally:
        if conn: conn.close()


def get_low_stock_medicines_db():
    """Get medicines where stock_quantity <= min_stock_level."""
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, name, packing_spec, price, stock_quantity, min_stock_level
            FROM medicines
            WHERE stock_quantity <= min_stock_level
            ORDER BY stock_quantity ASC
        """)
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_low_stock_medicines_db: {e}")
        return []
    finally:
        if conn: conn.close()


def get_medicine_usage_stats_db(year_month=None):
    """
    Get medicine usage statistics (total quantity used and total revenue).
    
    Args:
        year_month: Optional filter like '2026-03'. If None, returns all-time stats.
    
    Returns:
        List of rows: medicine_name, total_quantity, total_amount
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        if year_month:
            c.execute("""
                SELECT m.name as medicine_name,
                       SUM(pd.quantity) as total_quantity,
                       SUM(pd.quantity * pd.unit_price) as total_amount
                FROM prescription_details pd
                JOIN medicines m ON pd.medicine_id = m.id
                JOIN prescriptions_header ph ON pd.prescription_header_id = ph.id
                WHERE strftime('%Y-%m', ph.prescription_date) = ?
                GROUP BY pd.medicine_id
                ORDER BY total_quantity DESC
            """, (year_month,))
        else:
            c.execute("""
                SELECT m.name as medicine_name,
                       SUM(pd.quantity) as total_quantity,
                       SUM(pd.quantity * pd.unit_price) as total_amount
                FROM prescription_details pd
                JOIN medicines m ON pd.medicine_id = m.id
                GROUP BY pd.medicine_id
                ORDER BY total_quantity DESC
            """)
        
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_medicine_usage_stats_db: {e}")
        return []
    finally:
        if conn: conn.close()

# --- Statistics ---
def get_distinct_months_years():
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('''
            SELECT DISTINCT strftime('%Y-%m', visit_date) as m
            FROM (
                SELECT created_at as visit_date FROM patients
                UNION
                SELECT prescription_date as visit_date FROM prescriptions_header
            )
            WHERE m IS NOT NULL
            ORDER BY m DESC
        ''')
        rows_m = c.fetchall()
        months = [r['m'] for r in rows_m if r['m']]
        
        c.execute('''
            SELECT DISTINCT strftime('%Y', visit_date) as y
            FROM (
                SELECT created_at as visit_date FROM patients
                UNION
                SELECT prescription_date as visit_date FROM prescriptions_header
            )
            WHERE y IS NOT NULL
            ORDER BY y DESC
        ''')
        rows_y = c.fetchall()
        years = [r['y'] for r in rows_y if r['y']]
        
        return months, years
    except sqlite3.Error:
        return [], []
    finally:
        if conn: conn.close()

def get_stats_by_day_for_month(ym):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # [v5.2.0] Optimize: Use indexed range query instead of strftime function
        # ym format: 'YYYY-MM'
        try:
            year, month = map(int, ym.split('-'))
            start_date = f"{year:04d}-{month:02d}-01 00:00:00"
            if month == 12:
                end_date = f"{year+1:04d}-01-01 00:00:00"
            else:
                end_date = f"{year:04d}-{month+1:02d}-01 00:00:00"
            
            query = "SELECT DATE(created_at) as visit_date, COUNT(*) as count FROM patients WHERE created_at >= ? AND created_at < ? GROUP BY visit_date ORDER BY visit_date DESC"
            c.execute(query, (start_date, end_date))
        except (ValueError, IndexError):
            # Fallback to legacy if format is weird
            query = "SELECT DATE(created_at) as visit_date, COUNT(*) as count FROM patients WHERE strftime('%Y-%m', created_at) = ? GROUP BY visit_date ORDER BY visit_date DESC"
            c.execute(query, (ym,))
            
        rows = c.fetchall()
        result = [dict(r) for r in rows]
        return result
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_stats_by_week(limit=52):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        query = "SELECT strftime('%Y-W%W', created_at) as week, COUNT(*) as count FROM patients GROUP BY week ORDER BY week DESC LIMIT ?"
        c.execute(query, (limit,))
        rows = c.fetchall()
        result = [dict(r) for r in rows]
        return result
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_stats_by_month(limit=24):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        query = "SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as count FROM patients GROUP BY month ORDER BY month DESC LIMIT ?"
        c.execute(query, (limit,))
        rows = c.fetchall()
        result = [dict(r) for r in rows]
        return result
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_stats_by_year():
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        query = "SELECT strftime('%Y', created_at) as year, COUNT(*) as count FROM patients GROUP BY year ORDER BY year DESC"
        c.execute(query)
        rows = c.fetchall()
        result = [dict(r) for r in rows]
        return result
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_stats_by_gender():
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT gender, COUNT(*) as count FROM patients WHERE gender IS NOT NULL AND gender != '' GROUP BY gender")
        rows = c.fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_stats_by_location(limit=20):
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT address as location, COUNT(*) as count FROM patients GROUP BY location ORDER BY count DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        return [dict(r) for r in rows]
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_patient_dobs_by_time(filter_type, time_value):
    conn = None
    results = []
    where_clause = ""
    params = []

    if filter_type == "month": 
        # time_value format: 'YYYY-MM'
        try:
            year, month = map(int, time_value.split('-'))
            start_date = f"{year:04d}-{month:02d}-01 00:00:00"
            if month == 12:
                end_date = f"{year+1:04d}-01-01 00:00:00"
            else:
                end_date = f"{year:04d}-{month+1:02d}-01 00:00:00"
            where_clause = "WHERE created_at >= ? AND created_at < ?"
            params = [start_date, end_date]
        except (ValueError, IndexError):
            where_clause = "WHERE strftime('%Y-%m', created_at) = ?"
            params.append(time_value)
    elif filter_type == "year": 
        # time_value format: 'YYYY'
        try:
            year = int(time_value)
            start_date = f"{year:04d}-01-01 00:00:00"
            end_date = f"{year+1:04d}-01-01 00:00:00"
            where_clause = "WHERE created_at >= ? AND created_at < ?"
            params = [start_date, end_date]
        except ValueError:
            where_clause = "WHERE strftime('%Y', created_at) = ?"
            params.append(time_value)

    try:
        conn = _get_db_connection()
        c = conn.cursor()
        query = f'''
            SELECT dob, COUNT(*) as count
            FROM patients
            {where_clause}
            GROUP BY dob
        '''
        c.execute(query, tuple(params))
        rows = c.fetchall()
        results = [dict(r) for r in rows]
    except sqlite3.Error:
        pass
    finally:
        if conn: conn.close()
    return results

# =============================================================================
# PRESCRIPTION MIGRATION & CRUD FUNCTIONS (v4.3.4)
# =============================================================================

def _parse_legacy_medical_history(text):
    """
    Parse legacy medical_history format into diagnosis and medicine list.
    
    Input:  "Viêm họng cấp\n1) Amoxicillin x 10 Viên\n2) Paracetamol x 5"
    Output: {
        'diagnosis': 'Viêm họng cấp',
        'medicines': [
            {'name': 'Amoxicillin', 'qty': 10, 'spec': 'Viên'},
            {'name': 'Paracetamol', 'qty': 5, 'spec': ''}
        ]
    }
    """
    if not text or not text.strip():
        return {'diagnosis': '', 'medicines': []}
    
    lines = text.strip().split('\n')
    diagnosis = lines[0].strip() if lines else ''
    
    medicines = []
    # Regex: "số) Tên thuốc x SL Quy cách"
    pattern = r'^\d+\)\s*(.+?)\s+x\s+(\d+)\s*(.*)$'
    
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            try:
                qty = int(match.group(2))
                if qty > 0:
                    medicines.append({
                        'name': match.group(1).strip(),
                        'qty': qty,
                        'spec': match.group(3).strip()
                    })
            except ValueError:
                print(f"[DB MIGRATE] Warning: Invalid quantity in line: {line}")
                continue
        else:
            # Line doesn't match pattern - might be part of diagnosis
            # Skip it but log for debugging
            print(f"[DB MIGRATE] Skipping unparseable line: {line}")
    
    return {'diagnosis': diagnosis, 'medicines': medicines}


def _migrate_legacy_prescriptions():
    """
    Migrate legacy medical_history data to new prescription tables.
    This function is idempotent - safe to run multiple times.
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # Find patients with legacy data that haven't been migrated yet
        c.execute("""
            SELECT id, medical_history, created_at 
            FROM patients 
            WHERE prescription_migrated = 0 
              AND medical_history IS NOT NULL 
              AND medical_history != ''
        """)
        patients_to_migrate = c.fetchall()
        
        if not patients_to_migrate:
            return
        
        print(f"[DB MIGRATE] Found {len(patients_to_migrate)} patients to migrate...")
        migrated_count = 0
        
        for patient in patients_to_migrate:
            patient_id = patient['id']
            medical_history = patient['medical_history']
            created_at = patient['created_at']
            
            parsed = _parse_legacy_medical_history(medical_history)
            
            # Update patient's diagnosis field
            if parsed['diagnosis']:
                c.execute("UPDATE patients SET diagnosis = ? WHERE id = ?", 
                         (parsed['diagnosis'], patient_id))
            
            # Create prescription if there are medicines
            if parsed['medicines']:
                # Insert prescription header
                c.execute("""
                    INSERT INTO prescriptions_header 
                    (patient_id, prescription_date, diagnosis, total_amount, notes)
                    VALUES (?, ?, ?, 0, 'Migrated from legacy data')
                """, (patient_id, created_at, parsed['diagnosis']))
                
                prescription_id = c.lastrowid
                total_amount = 0
                
                # Insert prescription details
                for med in parsed['medicines']:
                    # Try to find medicine in database
                    c.execute("SELECT id, price FROM medicines WHERE LOWER(name) = LOWER(?)", 
                             (med['name'],))
                    medicine_row = c.fetchone()
                    
                    if medicine_row:
                        medicine_id = medicine_row['id']
                        unit_price = medicine_row['price'] or 0
                    else:
                        # Medicine not found - create it with price 0
                        c.execute("""
                            INSERT INTO medicines (name, packing_spec, price) 
                            VALUES (?, ?, 0)
                        """, (med['name'], med['spec']))
                        medicine_id = c.lastrowid
                        unit_price = 0
                        print(f"[DB MIGRATE] Created new medicine: {med['name']}")
                        
                        # [SYNC FIX] Must sync this new medicine immediately 
                        # so that prescription_details doesn't fail with FK constraint error
                        c.execute("SELECT * FROM medicines WHERE id=?", (medicine_id,))
                        new_med = c.fetchone()
                        if new_med:
                            from sync_manager import sync_manager
                            sync_manager.sync_medicine(new_med)
                    
                    # Insert detail record
                    c.execute("""
                        INSERT INTO prescription_details 
                        (prescription_header_id, medicine_id, quantity, unit_price)
                        VALUES (?, ?, ?, ?)
                    """, (prescription_id, medicine_id, med['qty'], unit_price))
                    
                    total_amount += med['qty'] * unit_price
                
                # Update total amount
                c.execute("UPDATE prescriptions_header SET total_amount = ? WHERE id = ?",
                         (total_amount, prescription_id))
            
            # Mark as migrated
            c.execute("UPDATE patients SET prescription_migrated = 1 WHERE id = ?", 
                     (patient_id,))
            migrated_count += 1
        
        conn.commit()
        print(f"[DB MIGRATE] Successfully migrated {migrated_count} patients.")
        
    except sqlite3.Error as e:
        print(f"[DB MIGRATE ERROR] {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
    finally:
        if conn: 
            conn.close()


def create_prescription_db(patient_id, diagnosis, items, notes=""):
    """
    Create a new prescription for a patient.
    
    Args:
        patient_id: ID of the patient
        diagnosis: Diagnosis for this prescription
        items: List of dicts with keys: medicine_id, quantity, unit_price
        notes: Optional notes
    
    Returns:
        prescription_id or None if error
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # Calculate total amount
        total_amount = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in items)
        
        # Insert prescription header
        c.execute("""
            INSERT INTO prescriptions_header 
            (patient_id, diagnosis, total_amount, notes)
            VALUES (?, ?, ?, ?)
        """, (patient_id, diagnosis, total_amount, notes))
        
        prescription_id = c.lastrowid
        
        # Insert prescription details + deduct stock
        for item in items:
            c.execute("""
                INSERT INTO prescription_details 
                (prescription_header_id, medicine_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (prescription_id, item['medicine_id'], item['quantity'], item['unit_price']))
            
            # [v5.1.0] Deduct stock in the same transaction
            c.execute("UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?",
                      (item['quantity'], item['medicine_id']))
        
        # Update patient's diagnosis field with latest
        c.execute("UPDATE patients SET diagnosis = ? WHERE id = ?", (diagnosis, patient_id))
        
        # Fetch data for sync BEFORE commit
        c.execute("SELECT * FROM prescriptions_header WHERE id=?", (prescription_id,))
        header = c.fetchone()
        
        c.execute("SELECT * FROM prescription_details WHERE prescription_header_id=?", (prescription_id,))
        details = c.fetchall()
        
        c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        patient = c.fetchone()
        
        # COMMIT FIRST - ensure local data is saved
        conn.commit()
        
        # [SYNC] Only sync AFTER commit succeeds (Fix Race Condition & Transaction Propagation Error)
        if header:
            sync_manager.sync_prescription_header(header)
        for d in details:
            sync_manager.sync_prescription_detail(d)
        if patient:
            sync_manager.sync_patient(patient)
        
        print(f"[DB] Created prescription {prescription_id} for patient {patient_id}")
        return prescription_id
        
    except sqlite3.Error as e:
        print(f"[DB ERROR] create_prescription_db: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        return None
    finally:
        if conn: 
            conn.close()


def get_latest_prescription_id_db(patient_id):
    """Get the ID of the most recent prescription for a patient."""
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id FROM prescriptions_header
            WHERE patient_id = ?
            ORDER BY prescription_date DESC
            LIMIT 1
        """, (patient_id,))
        row = c.fetchone()
        return row['id'] if row else None
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_latest_prescription_id_db: {e}")
        return None
    finally:
        if conn:
            conn.close()


def append_items_to_prescription_db(prescription_id, items):
    """
    Append new medicine items to an existing prescription.
    
    Args:
        prescription_id: ID of the existing prescription header
        items: List of dicts with keys: medicine_id, quantity, unit_price
    
    Returns:
        True on success, False on error
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # Calculate additional amount
        added_amount = sum(item.get('quantity', 0) * item.get('unit_price', 0) for item in items)
        
        detail_ids_to_sync = []
        
        # Insert new detail rows + deduct stock
        for item in items:
            c.execute("""
                INSERT INTO prescription_details
                (prescription_header_id, medicine_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (prescription_id, item['medicine_id'], item['quantity'], item['unit_price']))
            
            detail_ids_to_sync.append(c.lastrowid)
            
            # [v5.1.0] Deduct stock in the same transaction
            c.execute("UPDATE medicines SET stock_quantity = stock_quantity - ? WHERE id = ?",
                      (item['quantity'], item['medicine_id']))
        
        # Update total_amount on header
        c.execute("""
            UPDATE prescriptions_header
            SET total_amount = total_amount + ?
            WHERE id = ?
        """, (added_amount, prescription_id))
        
        # Fetch data for sync BEFORE commit
        c.execute("SELECT * FROM prescriptions_header WHERE id=?", (prescription_id,))
        header = c.fetchone()
        
        # Only fetch the NEWLY added details (Batch IN query is faster than looping)
        new_details = []
        if detail_ids_to_sync:
            # Prepare placeholders for IN clause
            placeholders = ','.join(['?'] * len(detail_ids_to_sync))
            c.execute(f"SELECT * FROM prescription_details WHERE id IN ({placeholders})", detail_ids_to_sync)
            new_details = c.fetchall()
        
        conn.commit()
        
        # [SYNC] Only sync the header and NEW details
        if header:
            sync_manager.sync_prescription_header(header)
        for d in new_details:
            sync_manager.sync_prescription_detail(d)
        
        print(f"[DB] Appended {len(items)} items to prescription {prescription_id}")
        return True
        
    except sqlite3.Error as e:
        print(f"[DB ERROR] append_items_to_prescription_db: {e}")
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()


def get_prescriptions_by_patient_db(patient_id):
    """
    Get all prescriptions for a patient with details.
    Uses batch fetch for details to avoid N+1 queries.
    
    Returns: List of prescription dicts with nested items
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # 1. Get prescription headers
        c.execute("""
            SELECT id, prescription_date, diagnosis, total_amount, notes
            FROM prescriptions_header
            WHERE patient_id = ?
            ORDER BY prescription_date DESC
        """, (patient_id,))
        
        headers = [dict(row) for row in c.fetchall()]
        if not headers:
            return []
            
        header_ids = [h['id'] for h in headers]
        
        # 2. Get ALL details for ALL headers in ONE query
        placeholders = ','.join(['?'] * len(header_ids))
        c.execute(f"""
            SELECT pd.id, pd.prescription_header_id, pd.medicine_id, pd.quantity, pd.unit_price,
                   m.name as medicine_name, m.packing_spec
            FROM prescription_details pd
            LEFT JOIN medicines m ON pd.medicine_id = m.id
            WHERE pd.prescription_header_id IN ({placeholders})
        """, header_ids)
        
        all_details = c.fetchall()
        
        # 3. Group details by header_id using a Dict
        details_by_header = {}
        for row in all_details:
            detail = dict(row)
            hid = detail['prescription_header_id']
            if hid not in details_by_header:
                details_by_header[hid] = []
            details_by_header[hid].append(detail)
            
        # 4. Map details back to headers
        for h in headers:
            h['items'] = details_by_header.get(h['id'], [])
            
        return headers
        
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_prescriptions_by_patient_db: {e}")
        return []
    finally:
        if conn: 
            conn.close()


def get_patient_diagnosis_db(patient_id):
    """Get the current diagnosis for a patient."""
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT diagnosis FROM patients WHERE id = ?", (patient_id,))
        row = c.fetchone()
        return row['diagnosis'] if row and row['diagnosis'] else ''
    except sqlite3.Error:
        return ''
    finally:
        if conn: 
            conn.close()


def set_patient_diagnosis_db(patient_id, diagnosis):
    """Set the diagnosis for a patient (separate from medical_history)."""
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE patients SET diagnosis = ? WHERE id = ?", (diagnosis, patient_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] set_patient_diagnosis_db: {e}")
        return False
    finally:
        if conn: 
            conn.close()


def update_patient_medical_history_db(patient_id, medical_history_text):
    """
    Update legacy medical_history field for backward compatibility.
    This ensures "Sửa Chẩn Đoán" form and Kotlin app can read prescriptions.
    
    Args:
        patient_id: ID of the patient
        medical_history_text: Legacy format text (e.g., "Diagnosis\n1) Med A x 10\n2) Med B x 5")
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE patients SET medical_history=? WHERE id=?', 
                  (medical_history_text, patient_id))
        
        # Fetch updated patient for sync
        c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        patient = c.fetchone()
        
        conn.commit()
        
        # [SYNC] Only sync AFTER commit succeeds (Fix Race Condition pattern)
        if patient:
            sync_manager.sync_patient(dict(patient))
        
        print(f"[DB] Updated medical_history for patient {patient_id}")
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] update_patient_medical_history_db: {e}")
        return False
    finally:
        if conn: 
            conn.close()

# =============================================================================
# CLOUD IMPORT FUNCTIONS (v4.5 - Two-Way Sync)
# These functions insert data from Cloud WITHOUT triggering sync back.
# =============================================================================

def get_all_patient_ids():
    """Get all patient IDs from local database for sync comparison."""
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM patients")
        return [row['id'] for row in c.fetchall()]
    except sqlite3.Error:
        return []
    finally:
        if conn: conn.close()

def get_patients_by_ids(pids):
    """Fetch multiple patients by their IDs in a single batch query."""
    if not pids:
        return []
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        placeholders = ','.join(['?'] * len(pids))
        c.execute(f"SELECT * FROM patients WHERE id IN ({placeholders})", tuple(pids))
        return [dict(row) for row in c.fetchall()]
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_patients_by_ids: {e}")
        return []
    finally:
        if conn: conn.close()

def insert_patient_from_cloud(data):
    """
    Insert a patient record from Cloud data.
    IMPORTANT: Does NOT trigger sync_manager to avoid infinite loops.
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # Extract fields with defaults for missing columns
        name_normalized = utils.remove_diacritics(data.get('name', '').lower()) if data.get('name') else None
        
        c.execute('''INSERT OR REPLACE INTO patients 
                     (id, name, dob, gender, address, phone, weight, medical_history, created_at, name_normalized, diagnosis)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data.get('id'),
                   data.get('name'),
                   data.get('dob'),
                   data.get('gender'),
                   data.get('address'),
                   data.get('phone'),
                   data.get('weight'),
                   data.get('medical_history'),
                   data.get('created_at'),
                   name_normalized,
                   data.get('diagnosis')))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_patient_from_cloud: {e}")
        return False
    finally:
        if conn: conn.close()

def insert_medicine_from_cloud(data):
    """
    Insert a medicine record from Cloud data.
    IMPORTANT: Does NOT trigger sync_manager to avoid infinite loops.
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO medicines (id, name, packing_spec, price, stock_quantity, min_stock_level)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (data.get('id'),
                   data.get('name'),
                   data.get('packing_spec'),
                   data.get('price'),
                   data.get('stock_quantity', 0),
                   data.get('min_stock_level', 5)))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_medicine_from_cloud: {e}")
        return False
    finally:
        if conn: conn.close()

def insert_prescription_header_from_cloud(data):
    """
    Insert a prescription header from Cloud data.
    IMPORTANT: Does NOT trigger sync_manager to avoid infinite loops.
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO prescriptions_header 
                     (id, patient_id, prescription_date, diagnosis, total_amount, notes)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (data.get('id'),
                   data.get('patient_id'),
                   data.get('prescription_date'),
                   data.get('diagnosis'),
                   data.get('total_amount'),
                   data.get('notes')))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_prescription_header_from_cloud: {e}")
        return False
    finally:
        if conn: conn.close()

def insert_prescription_detail_from_cloud(data):
    """
    Insert a prescription detail from Cloud data.
    IMPORTANT: Does NOT trigger sync_manager to avoid infinite loops.
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO prescription_details 
                     (id, prescription_header_id, medicine_id, quantity, unit_price)
                     VALUES (?, ?, ?, ?, ?)''',
                  (data.get('id'),
                   data.get('prescription_header_id'),
                   data.get('medicine_id'),
                   data.get('quantity'),
                   data.get('unit_price')))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_prescription_detail_from_cloud: {e}")
        return False
    finally:
        if conn: conn.close()

# --- Bulk Operations (v5.2.0) ---

def insert_patients_bulk(data_list):
    """Bulk insert patients from Cloud data."""
    if not data_list:
        return True
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # Prepare params
        params = []
        for data in data_list:
            # Compute normalized name for indexed search
            name_normalized = utils.remove_diacritics(data.get('name', '').lower()) if data.get('name') else None
            params.append((
                data.get('id'),
                data.get('name'),
                data.get('dob'),
                data.get('gender'),
                data.get('address'),
                data.get('phone'),
                data.get('weight'),
                data.get('medical_history'),
                data.get('created_at'),
                name_normalized,
                data.get('diagnosis')
            ))
            
        c.executemany('''INSERT OR REPLACE INTO patients 
                         (id, name, dob, gender, address, phone, weight, medical_history, created_at, name_normalized, diagnosis)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_patients_bulk: {e}")
        return False
    finally:
        if conn: conn.close()

def insert_medicines_bulk(data_list):
    """Bulk insert medicines from Cloud or Excel data."""
    if not data_list:
        return True
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        params = []
        for data in data_list:
            params.append((
                data.get('id'), # May be None if importing from Excel
                data.get('name'),
                data.get('packing_spec'),
                data.get('price', 0.0),
                data.get('stock_quantity', 0),
                data.get('min_stock_level', 5)
            ))
            
        c.executemany('''INSERT OR REPLACE INTO medicines (id, name, packing_spec, price, stock_quantity, min_stock_level)
                         VALUES (?, ?, ?, ?, ?, ?)''', params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_medicines_bulk: {e}")
        return False
    finally:
        if conn: conn.close()

def insert_headers_bulk(data_list):
    """Bulk insert prescription headers from Cloud data."""
    if not data_list:
        return True
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        params = []
        for data in data_list:
            params.append((
                data.get('id'),
                data.get('patient_id'),
                data.get('prescription_date'),
                data.get('diagnosis'),
                data.get('total_amount'),
                data.get('notes')
            ))
            
        c.executemany('''INSERT OR REPLACE INTO prescriptions_header 
                         (id, patient_id, prescription_date, diagnosis, total_amount, notes)
                         VALUES (?, ?, ?, ?, ?, ?)''', params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_headers_bulk: {e}")
        return False
    finally:
        if conn: conn.close()

def insert_details_bulk(data_list):
    """Bulk insert prescription details from Cloud data."""
    if not data_list:
        return True
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        params = []
        for data in data_list:
            params.append((
                data.get('id'),
                data.get('prescription_header_id'),
                data.get('medicine_id'),
                data.get('quantity'),
                data.get('unit_price')
            ))
            
        c.executemany('''INSERT OR REPLACE INTO prescription_details 
                         (id, prescription_header_id, medicine_id, quantity, unit_price)
                         VALUES (?, ?, ?, ?, ?)''', params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] insert_details_bulk: {e}")
        return False
    finally:
        if conn: conn.close()
