"""
Quick Test: Recent Bug Fixes
=============================
Test 1: update_visit_details_db() phải cập nhật cả cột 'diagnosis'
Test 2: Logic 'Kê tiếp đơn cũ' phải nối thêm thuốc mới vào đơn cũ
"""
import sqlite3
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import database

PASS = 0
FAIL = 0

def test_pass(name):
    global PASS
    PASS += 1
    print(f"  ✅ PASS: {name}")

def test_fail(name, detail=""):
    global FAIL
    FAIL += 1
    print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"     → {detail}")

# ============================================================
# TEST 1: update_visit_details_db cập nhật cả diagnosis column
# ============================================================
print("\n🧪 Test 1: update_visit_details_db() cập nhật cột 'diagnosis'")
print("-" * 60)

# Setup: tạo bệnh nhân test
test_patient_name = "__TEST_DIAG_FIX__"
database.add_patient_db(test_patient_name, "2000-01-01", "Nam", "Test", "0000000000", "10", "Old diagnosis")

# Tìm bệnh nhân vừa tạo
conn = sqlite3.connect(config.get_database_path())
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute("SELECT id FROM patients WHERE name = ? ORDER BY id DESC LIMIT 1", (test_patient_name,))
row = c.fetchone()

if not row:
    test_fail("Không tạo được bệnh nhân test")
else:
    test_id = row['id']
    
    # Chạy update_visit_details_db với chẩn đoán mới
    new_full_text = "Viêm họng cấp\n1) Amoxicillin x 10 Viên"
    result = database.update_visit_details_db(test_id, "12", new_full_text)
    
    if not result:
        test_fail("update_visit_details_db trả về False")
    else:
        test_pass("update_visit_details_db trả về True")
    
    # Kiểm tra cột diagnosis có được cập nhật không
    c.execute("SELECT diagnosis, medical_history FROM patients WHERE id = ?", (test_id,))
    updated = c.fetchone()
    
    if updated['medical_history'] == new_full_text:
        test_pass("medical_history được cập nhật đúng")
    else:
        test_fail("medical_history không đúng", f"Expected: '{new_full_text}', Got: '{updated['medical_history']}'")
    
    if updated['diagnosis'] == "Viêm họng cấp":
        test_pass("diagnosis column được cập nhật đúng (dòng đầu tiên)")
    else:
        test_fail("diagnosis column KHÔNG được cập nhật!", f"Expected: 'Viêm họng cấp', Got: '{updated['diagnosis']}'")
    
    # Cleanup
    c.execute("DELETE FROM patients WHERE id = ?", (test_id,))
    conn.commit()

conn.close()

# ============================================================
# TEST 2: Logic 'Kê tiếp đơn cũ' (append mode)  
# ============================================================
print("\n🧪 Test 2: Logic 'Kê tiếp đơn cũ' (append mode)")
print("-" * 60)

import re

# Simulate existing medical_history
existing_history = "Viêm họng cấp\n1) Amoxicillin x 10 Viên\n2) Paracetamol x 5 Viên"

# Simulate new prescription items
new_items = [
    {'name': 'Ibuprofen', 'qty': 3, 'spec': 'Viên'},
    {'name': 'Vitamin C', 'qty': 6, 'spec': 'Viên'},
]

# --- Reproduce the APPEND logic from save_prescription ---
existing_lines = existing_history.split('\n') if existing_history else []
old_med_lines = [l for l in existing_lines if re.match(r'^\s*\d+\)', l)]
start_num = len(old_med_lines) + 1

new_med_lines = []
for i, item in enumerate(new_items):
    new_med_lines.append(f"{start_num + i}) {item['name']} x {item['qty']} {item['spec']}")

legacy_text = existing_history + "\n" + "\n".join(new_med_lines)

# Verify
expected = (
    "Viêm họng cấp\n"
    "1) Amoxicillin x 10 Viên\n"
    "2) Paracetamol x 5 Viên\n"
    "3) Ibuprofen x 3 Viên\n"
    "4) Vitamin C x 6 Viên"
)

if legacy_text == expected:
    test_pass("Append mode: thuốc mới được nối đúng vị trí (3, 4)")
else:
    test_fail("Append mode sai kết quả", f"\nExpected:\n{expected}\n\nGot:\n{legacy_text}")

# Verify numbering
all_med_lines = [l for l in legacy_text.split('\n') if re.match(r'^\s*\d+\)', l)]
if len(all_med_lines) == 4:
    test_pass("Tổng cộng 4 dòng thuốc (2 cũ + 2 mới)")
else:
    test_fail("Số dòng thuốc sai", f"Expected 4, Got {len(all_med_lines)}")

# Check numbering is sequential
numbers = [int(re.match(r'^\s*(\d+)\)', l).group(1)) for l in all_med_lines]
if numbers == [1, 2, 3, 4]:
    test_pass("Số thứ tự liên tục: 1, 2, 3, 4")
else:
    test_fail("Số thứ tự không liên tục", f"Got: {numbers}")

# --- Test REPLACE logic (when checkbox not checked) ---
print("\n🧪 Test 2b: Logic thay thế bình thường (không tích checkbox)")
print("-" * 60)

current_diagnosis = "Viêm họng cấp"
legacy_lines = [current_diagnosis]
for i, item in enumerate(new_items):
    legacy_lines.append(f"{i+1}) {item['name']} x {item['qty']} {item['spec']}")
replace_text = "\n".join(legacy_lines)

expected_replace = (
    "Viêm họng cấp\n"
    "1) Ibuprofen x 3 Viên\n"
    "2) Vitamin C x 6 Viên"
)

if replace_text == expected_replace:
    test_pass("Replace mode: chỉ có thuốc mới (1, 2)")
else:
    test_fail("Replace mode sai", f"\nExpected:\n{expected_replace}\n\nGot:\n{replace_text}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 60)
total = PASS + FAIL
if FAIL == 0:
    print(f"🎉 KẾT QUẢ: {PASS}/{total} tests PASS - Tất cả OK!")
else:
    print(f"⚠️  KẾT QUẢ: {PASS}/{total} tests PASS, {FAIL} FAIL")
print("=" * 60)

sys.exit(1 if FAIL > 0 else 0)
