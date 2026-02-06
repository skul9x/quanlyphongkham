"""Check prescription details for headers 443 and 882"""
import sqlite3
conn = sqlite3.connect('clinic.db')
c = conn.cursor()

print("=== PRESCRIPTION DETAILS CHECK ===")
c.execute("SELECT * FROM prescription_details WHERE prescription_header_id IN (443, 882)")
details = c.fetchall()
print(f"Found {len(details)} details for headers 443, 882")
for d in details:
    print(f"  {d}")

print("\nSample prescription_details:")
c.execute("SELECT pd.*, m.name FROM prescription_details pd LEFT JOIN medicines m ON pd.medicine_id=m.id LIMIT 5")
for r in c.fetchall():
    print(f"  {r}")

conn.close()
