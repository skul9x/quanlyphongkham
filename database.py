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
        conn = sqlite3.connect(config.DATABASE_NAME, timeout=30)
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
        
        # [SYNC] Add to queue
        new_id = c.lastrowid
        c.execute("SELECT * FROM patients WHERE id=?", (new_id,))
        new_patient = c.fetchone()
        sync_manager.sync_patient(new_patient)
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DB ERROR] Add Patient: {e}")
        return False
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
        # [SYNC] Add to queue
        c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        updated_patient = c.fetchone()
        if updated_patient:
            sync_manager.sync_patient(updated_patient)

        conn.commit()
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
        c.execute('UPDATE patients SET weight=?, medical_history=? WHERE id=?', (weight, diagnosis, visit_id))
        conn.commit()
        return True
    except sqlite3.Error:
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
        # [SYNC]
        sync_manager.delete_patient(visit_id)
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
        
        # [SYNC] Process deletions
        for pid in ids_to_delete:
            sync_manager.delete_patient(pid)

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
        c.execute("SELECT id, name, packing_spec, price FROM medicines ORDER BY name COLLATE NOCASE")
        return c.fetchall()
    except sqlite3.Error as e:
        print(f"[DB ERROR] get_all_medicines_db: {e}")
        return []
    finally:
        if conn: conn.close()

def add_medicine_db(name, spec, price):
    print(f"[DB] add_medicine_db called: {name}, {spec}, {price}")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO medicines (name, packing_spec, price) VALUES (?, ?, ?)", (name, spec, price))
        c.execute("INSERT INTO medicines (name, packing_spec, price) VALUES (?, ?, ?)", (name, spec, price))
        new_id = c.lastrowid
        
        # [SYNC]
        c.execute("SELECT * FROM medicines WHERE id=?", (new_id,))
        new_med = c.fetchone()
        sync_manager.sync_medicine(new_med)
        
        conn.commit()
        print("[DB] Medicine added successfully, ID:", c.lastrowid)
        return c.lastrowid
    except sqlite3.Error as e:
        print(f"[DB ERROR] add_medicine_db: {e}")
        return None
    finally:
        if conn: conn.close()

def update_medicine_db(mid, name, spec, price):
    print(f"[DB] update_medicine_db called: ID={mid}, {name}, {spec}, {price}")
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE medicines SET name=?, packing_spec=?, price=? WHERE id=?", (name, spec, price, mid))
        
        # [SYNC]
        c.execute("SELECT * FROM medicines WHERE id=?", (mid,))
        updated_med = c.fetchone()
        sync_manager.sync_medicine(updated_med)

        conn.commit()
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
        c.execute("SELECT id, name, packing_spec, price FROM medicines WHERE id=?", (mid,))
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
        c.execute("SELECT id, name, packing_spec, price FROM medicines WHERE LOWER(name) = LOWER(?)", (name.strip(),))
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
        where_clause = "WHERE strftime('%Y-%m', created_at) = ?"
        params.append(time_value)
    elif filter_type == "year": 
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
        
        # Insert prescription details
        for item in items:
            c.execute("""
                INSERT INTO prescription_details 
                (prescription_header_id, medicine_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (prescription_id, item['medicine_id'], item['quantity'], item['unit_price']))
        
        # Update patient's diagnosis field with latest
        c.execute("UPDATE patients SET diagnosis = ? WHERE id = ?", (diagnosis, patient_id))
        
        # [SYNC] Sync Header
        c.execute("SELECT * FROM prescriptions_header WHERE id=?", (prescription_id,))
        header = c.fetchone()
        sync_manager.sync_prescription_header(header)
        
        # [SYNC] Sync Details
        for item in items:
             # Need to fetch the detail row properly or construct it
             # Simplest is to fetch all details for this header
             pass 
             
        c.execute("SELECT * FROM prescription_details WHERE prescription_header_id=?", (prescription_id,))
        details = c.fetchall()
        for d in details:
            sync_manager.sync_prescription_detail(d)
            
        # [SYNC] Sync Patient (diagnosis changed)
        c.execute("SELECT * FROM patients WHERE id=?", (patient_id,))
        p = c.fetchone()
        sync_manager.sync_patient(p)
        
        conn.commit()
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


def get_prescriptions_by_patient_db(patient_id):
    """
    Get all prescriptions for a patient with details.
    
    Returns: List of prescription dicts with nested items
    """
    conn = None
    try:
        conn = _get_db_connection()
        c = conn.cursor()
        
        # Get prescription headers
        c.execute("""
            SELECT id, prescription_date, diagnosis, total_amount, notes
            FROM prescriptions_header
            WHERE patient_id = ?
            ORDER BY prescription_date DESC
        """, (patient_id,))
        
        prescriptions = []
        for row in c.fetchall():
            prescription = dict(row)
            
            # Get details for this prescription
            c.execute("""
                SELECT pd.id, pd.medicine_id, pd.quantity, pd.unit_price,
                       m.name as medicine_name, m.packing_spec
                FROM prescription_details pd
                LEFT JOIN medicines m ON pd.medicine_id = m.id
                WHERE pd.prescription_header_id = ?
            """, (prescription['id'],))
            
            prescription['items'] = [dict(item) for item in c.fetchall()]
            prescriptions.append(prescription)
        
        return prescriptions
        
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
        c.execute('''INSERT OR REPLACE INTO medicines (id, name, packing_spec, price)
                     VALUES (?, ?, ?, ?)''',
                  (data.get('id'),
                   data.get('name'),
                   data.get('packing_spec'),
                   data.get('price')))
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
