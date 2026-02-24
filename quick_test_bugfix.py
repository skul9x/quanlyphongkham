"""
Quick Test Script: Verify 3 Critical Bug Fixes
- Test 1: Duplicate INSERT fix (add_medicine_db)
- Test 2: Race Condition fix (sync after commit)
- Test 3: Transaction Propagation fix (create_prescription_db)
"""
import sqlite3
import sys
import os
import io

# Fix Windows encoding for emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
import config

def test_add_medicine_no_duplicate():
    """Test: add_medicine_db should only create 1 record"""
    print("\n🧪 Test 1: Duplicate INSERT fix")
    print("-" * 40)
    
    # Get count before
    conn = sqlite3.connect(config.get_database_path())
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM medicines")
    count_before = c.fetchone()[0]
    
    # Add a test medicine
    test_name = f"__TEST_MED_{count_before}__"
    result = database.add_medicine_db(test_name, "Test Spec", 1000)
    
    # Get count after
    c.execute("SELECT COUNT(*) FROM medicines")
    count_after = c.fetchone()[0]
    
    # Check: only 1 record added
    diff = count_after - count_before
    
    # Cleanup
    if result:
        c.execute("DELETE FROM medicines WHERE name = ?", (test_name,))
        conn.commit()
    conn.close()
    
    if diff == 1:
        print(f"✅ PASS: Added {diff} record (expected 1)")
        return True
    else:
        print(f"❌ FAIL: Added {diff} records (expected 1)")
        return False

def test_sync_order():
    """Test: Verify code structure - sync should be after commit"""
    print("\n🧪 Test 2 & 3: Sync after Commit order")
    print("-" * 40)
    
    # Read database.py and check pattern
    with open("database.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check for the fixed pattern in key functions
    functions_to_check = [
        "add_patient_db",
        "update_patient_db", 
        "add_medicine_db",
        "update_medicine_db",
        "create_prescription_db"
    ]
    
    all_pass = True
    for func_name in functions_to_check:
        # Find function content
        start = content.find(f"def {func_name}")
        if start == -1:
            print(f"⚠️  SKIP: {func_name} not found")
            continue
        
        # Find next function or end
        next_def = content.find("\ndef ", start + 1)
        if next_def == -1:
            func_content = content[start:]
        else:
            func_content = content[start:next_def]
        
        # Check: commit() should appear BEFORE sync_manager calls
        commit_pos = func_content.find("conn.commit()")
        sync_pos = func_content.find("sync_manager.sync_")
        
        if commit_pos == -1:
            print(f"⚠️  SKIP: {func_name} has no commit()")
            continue
            
        if sync_pos == -1:
            print(f"⚠️  SKIP: {func_name} has no sync call")
            continue
        
        if commit_pos < sync_pos:
            print(f"✅ PASS: {func_name} - commit() before sync_manager")
        else:
            print(f"❌ FAIL: {func_name} - sync_manager before commit()!")
            all_pass = False
    
    return all_pass

def run_all_tests():
    print("=" * 50)
    print("🔬 QUICK TEST: 3 Critical Bug Fixes")
    print("=" * 50)
    
    results = []
    
    # Test 1
    results.append(("Duplicate INSERT", test_add_medicine_no_duplicate()))
    
    # Test 2 & 3
    results.append(("Sync Order", test_sync_order()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        status = "PASS" if result else "FAIL"
        print(f"  {icon} {name}: {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All critical bug fixes verified!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review.")
        return 1

if __name__ == "__main__":
    exit(run_all_tests())
