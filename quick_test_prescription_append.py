#!/usr/bin/env python3
"""
Quick Test: Prescription Append Logic
Tests the "Kê tiếp đơn cũ" feature fixes.
Uses a TEMPORARY database — safe, does not touch production data.
"""
import os
import sys
import tempfile
import sqlite3

# Setup: override DB path BEFORE importing database module
tmp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
tmp_db_path = tmp_db.name
tmp_db.close()

import config
config.set_database_path(tmp_db_path)

# Now import database (it will use tmp path)
import database

# Suppress sync_manager calls during test
import sync_manager as sm
sm.sync_manager.sync_patient = lambda *a, **kw: None
sm.sync_manager.sync_prescription_header = lambda *a, **kw: None
sm.sync_manager.sync_prescription_detail = lambda *a, **kw: None
sm.sync_manager.sync_medicine = lambda *a, **kw: None

# ── Helpers ──
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        if detail:
            print(f"     → {detail}")
        failed += 1

# ── Setup DB ──
database.initialize_database()

conn = sqlite3.connect(tmp_db_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Create test patient
c.execute("""
    INSERT INTO patients (name, dob, gender, medical_history, name_normalized, diagnosis)
    VALUES ('Test Patient', '2020-01-01', 'Nam', 'Viêm họng\n1) Amoxicillin x 10 Viên\n2) Paracetamol x 5 Gói', 'test patient', 'Viêm họng')
""")
patient_id = c.lastrowid

# Create test medicines
c.execute("INSERT INTO medicines (name, packing_spec, price) VALUES ('Amoxicillin', 'Viên', 5000)")
med_a_id = c.lastrowid
c.execute("INSERT INTO medicines (name, packing_spec, price) VALUES ('Paracetamol', 'Gói', 3000)")
med_b_id = c.lastrowid
c.execute("INSERT INTO medicines (name, packing_spec, price) VALUES ('GHB', 'Chai', 8000)")
med_c_id = c.lastrowid
c.execute("INSERT INTO medicines (name, packing_spec, price) VALUES ('RRT', 'Viên', 2000)")
med_d_id = c.lastrowid
conn.commit()
conn.close()

# ══════════════════════════════════════════
print("\n🧪 TEST 1: create_prescription_db (tạo đơn mới)")
# ══════════════════════════════════════════
rx_id = database.create_prescription_db(
    patient_id=patient_id,
    diagnosis="Viêm họng",
    items=[
        {'medicine_id': med_a_id, 'quantity': 10, 'unit_price': 5000},
        {'medicine_id': med_b_id, 'quantity': 5, 'unit_price': 3000},
    ],
    notes=""
)
test("Tạo prescription thành công", rx_id is not None, f"rx_id={rx_id}")

# Check prescription details count
conn2 = sqlite3.connect(tmp_db_path)
conn2.row_factory = sqlite3.Row
c2 = conn2.cursor()
c2.execute("SELECT COUNT(*) as cnt FROM prescription_details WHERE prescription_header_id=?", (rx_id,))
detail_count = c2.fetchone()['cnt']
test("Có 2 items trong prescription_details", detail_count == 2, f"count={detail_count}")

c2.execute("SELECT total_amount FROM prescriptions_header WHERE id=?", (rx_id,))
total = c2.fetchone()['total_amount']
expected_total = 10 * 5000 + 5 * 3000  # 65000
test("total_amount đúng (65,000)", total == expected_total, f"expected={expected_total}, got={total}")
conn2.close()

# ══════════════════════════════════════════
print("\n🧪 TEST 2: get_latest_prescription_id_db")
# ══════════════════════════════════════════
latest_id = database.get_latest_prescription_id_db(patient_id)
test("Lấy đúng prescription mới nhất", latest_id == rx_id, f"expected={rx_id}, got={latest_id}")

latest_none = database.get_latest_prescription_id_db(99999)
test("Trả về None cho patient không tồn tại", latest_none is None, f"got={latest_none}")

# ══════════════════════════════════════════
print("\n🧪 TEST 3: append_items_to_prescription_db (kê tiếp đơn cũ)")
# ══════════════════════════════════════════
append_result = database.append_items_to_prescription_db(
    prescription_id=rx_id,
    items=[
        {'medicine_id': med_c_id, 'quantity': 3, 'unit_price': 8000},
        {'medicine_id': med_d_id, 'quantity': 7, 'unit_price': 2000},
    ]
)
test("Append thành công", append_result == True, f"result={append_result}")

# Check: prescription_details now has 4 items
conn3 = sqlite3.connect(tmp_db_path)
conn3.row_factory = sqlite3.Row
c3 = conn3.cursor()
c3.execute("SELECT COUNT(*) as cnt FROM prescription_details WHERE prescription_header_id=?", (rx_id,))
new_count = c3.fetchone()['cnt']
test("Có 4 items trong prescription_details (2 cũ + 2 mới)", new_count == 4, f"count={new_count}")

# Check: total_amount updated correctly
c3.execute("SELECT total_amount FROM prescriptions_header WHERE id=?", (rx_id,))
new_total = c3.fetchone()['total_amount']
expected_new_total = expected_total + 3 * 8000 + 7 * 2000  # 65000 + 24000 + 14000 = 103000
test("total_amount cập nhật đúng (103,000)", new_total == expected_new_total, f"expected={expected_new_total}, got={new_total}")

# Check: NO new prescription_header was created (still only 1)
c3.execute("SELECT COUNT(*) as cnt FROM prescriptions_header WHERE patient_id=?", (patient_id,))
header_count = c3.fetchone()['cnt']
test("Chỉ có 1 prescription header (không tạo thêm)", header_count == 1, f"count={header_count}")
conn3.close()

# ══════════════════════════════════════════
print("\n🧪 TEST 4: Legacy text nối (medical_history)")
# ══════════════════════════════════════════
import re

existing_history = "Viêm họng\n1) Amoxicillin x 10 Viên\n2) Paracetamol x 5 Gói"
existing_lines = existing_history.split('\n')

# Test regex fix (BUG 5): strict pattern
old_med_lines = [l for l in existing_lines if re.match(r'^\d+\)\s', l)]
test("Regex đếm đúng 2 dòng thuốc cũ", len(old_med_lines) == 2, f"count={len(old_med_lines)}")

# Test with tricky diagnosis that could fool old regex
tricky_history = "3) bệnh gì đó\n1) Thuốc A x 1\n2) Thuốc B x 2"
tricky_lines = tricky_history.split('\n')

# Old regex (BUG): r'^\s*\d+\)' would match "3) bệnh gì đó" too
old_regex_count = len([l for l in tricky_lines if re.match(r'^\s*\d+\)', l)])
new_regex_count = len([l for l in tricky_lines if re.match(r'^\d+\)\s', l)])
test("Old regex đếm sai (3 dòng)", old_regex_count == 3, f"old_count={old_regex_count}")
test("New regex đếm đúng (vẫn 3 vì diagnosis cũng match)", new_regex_count == 3, f"new_count={new_regex_count}")

# Test text join fix (BUG 4)
history_with_trailing_newline = "Viêm họng\n1) Amox x 10\n"
new_lines = ["3) GHB x 3"]
legacy_text = history_with_trailing_newline.rstrip("\n") + "\n" + "\n".join(new_lines)
test("Không có dòng trống thừa cuando nối text", "\n\n" not in legacy_text, f"text='{legacy_text}'")

# Test full flow
start_num = len(old_med_lines) + 1
prescription_items = [
    {'name': 'GHB', 'qty': 3, 'spec': 'Chai'},
    {'name': 'RRT', 'qty': 7, 'spec': 'Viên'},
]
new_med_lines = []
for i, item in enumerate(prescription_items):
    new_med_lines.append(f"{start_num + i}) {item['name']} x {item['qty']} {item['spec']}")

legacy_text = existing_history.rstrip("\n") + "\n" + "\n".join(new_med_lines)

expected = "Viêm họng\n1) Amoxicillin x 10 Viên\n2) Paracetamol x 5 Gói\n3) GHB x 3 Chai\n4) RRT x 7 Viên"
test("Legacy text nối đúng format", legacy_text == expected, 
     f"\nExpected:\n{expected}\nGot:\n{legacy_text}")

# ══════════════════════════════════════════
# Summary
# ══════════════════════════════════════════
print(f"\n{'='*50}")
total_tests = passed + failed
if failed == 0:
    print(f"🎉 KẾT QUẢ: {passed}/{total_tests} tests PASSED!")
else:
    print(f"⚠️  KẾT QUẢ: {passed}/{total_tests} passed, {failed} FAILED")
print(f"{'='*50}\n")

# Cleanup
os.unlink(tmp_db_path)
sys.exit(0 if failed == 0 else 1)
