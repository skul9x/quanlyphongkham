"""
Quick diagnostic script to check prescription data state for patient 588
"""
import sqlite3

print("=== PRESCRIPTION DEBUG FOR PATIENT 588 ===\n")

conn = sqlite3.connect('clinic.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 1. Check patient 588
print("[1] Patient 588 info:")
c.execute("SELECT id, name, diagnosis, prescription_migrated, medical_history FROM patients WHERE id=588")
p = c.fetchone()
if p:
    print(f"   Name: {p['name']}")
    print(f"   Diagnosis: {p['diagnosis']}")
    print(f"   prescription_migrated: {p['prescription_migrated']}")
    print(f"   medical_history: {repr(p['medical_history'][:100] if p['medical_history'] else None)}...")
else:
    print("   NOT FOUND!")

# 2. Check prescriptions for patient 588
print("\n[2] Prescriptions for patient 588:")
c.execute("SELECT * FROM prescriptions_header WHERE patient_id=588")
headers = c.fetchall()
print(f"   Found {len(headers)} prescription headers")
for h in headers:
    print(f"   - ID: {h['id']}, Date: {h['prescription_date']}, Diagnosis: {h['diagnosis']}")

# 3. Check if ANY prescriptions exist
print("\n[3] Total prescription counts:")
c.execute("SELECT COUNT(*) FROM prescriptions_header")
print(f"   Total headers: {c.fetchone()[0]}")
c.execute("SELECT COUNT(*) FROM prescription_details")
print(f"   Total details: {c.fetchone()[0]}")

# 4. Sample some prescription patient_ids
print("\n[4] Sample patient_ids in prescriptions_header:")
c.execute("SELECT DISTINCT patient_id FROM prescriptions_header LIMIT 10")
print(f"   {[r[0] for r in c.fetchall()]}")

# 5. Check what patient_id formats look like
print("\n[5] First 5 patients with prescriptions:")
c.execute("""
    SELECT p.id, p.name, COUNT(ph.id) as rx_count 
    FROM patients p 
    JOIN prescriptions_header ph ON p.id = ph.patient_id 
    GROUP BY p.id 
    LIMIT 5
""")
for r in c.fetchall():
    print(f"   Patient {r['id']} ({r['name']}): {r['rx_count']} prescriptions")

conn.close()
print("\n=== END DEBUG ===")
