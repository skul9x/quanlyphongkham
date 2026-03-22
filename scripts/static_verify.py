import ast
import os

def check_file(filename):
    if not os.path.exists(filename):
        print(f"ERROR: File {filename} not found.")
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return ast.parse(f.read())

def test_phase_1():
    print("\n--- [PHASE 1: DB RETURN LOGIC] ---")
    tree = check_file("database.py")
    if not tree: return
    
    found = False
    for node in ast.walk(tree):
        # We are using add_patient_db for adding visits in this app structure
        if isinstance(node, ast.FunctionDef) and node.name == "add_patient_db":
            for sub_node in ast.walk(node):
                if isinstance(sub_node, ast.Return):
                    found = True
                    print(f"PASS: Found return statement in add_patient_db")
                    if isinstance(sub_node.value, ast.Name):
                        print(f"PASS: Returns variable: {sub_node.value.id}")
    if not found:
        print("FAIL: add_patient_db function not found or has no return.")

def test_phase_2():
    print("\n--- [PHASE 2: UI CALLBACK LOGIC] ---")
    tree = check_file("ui_add_visit_window_pyside.py")
    if not tree: return
    
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr == "on_success_callback":
                found = True
                # Check for args or keywords
                arg_count = len(node.args)
                kw_count = len(node.keywords)
                print(f"PASS: Found callback call with {arg_count} args and {kw_count} keywords.")
                
                # Check if 'action' and 'new_id' are in keywords
                kws = [k.arg for k in node.keywords]
                if 'action' in kws and 'new_id' in kws:
                    print("PASS: Callback keywords match Phase 2 requirement (action, new_id).")
                elif arg_count >= 2:
                    print("PASS: Callback positional args match.")
                else:
                    print(f"FAIL: Callback signature mismatch. Keywords found: {kws}")
    if not found:
        print("FAIL: on_success_callback invocation not found.")

def test_phase_3():
    print("\n--- [PHASE 3: MAIN SCREEN INTEGRATION] ---")
    tree = check_file("ui_patient_pyside.py")
    if not tree: return
    
    found_method = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "refresh_current":
            found_method = True
            args = [arg.arg for arg in node.args.args]
            print(f"PASS: Found refresh_current with args: {args}")
            if 'action' in args and 'new_id' in args:
                print("PASS: refresh_current accepts action and new_id.")
            
            # Check for timing logic (QTimer.singleShot)
            has_timer = any(isinstance(sn, ast.Attribute) and sn.attr == "singleShot" for sn in ast.walk(node))
            if has_timer:
                print("PASS: Found QTimer.singleShot delay logic.")

    if not found_method:
        print("FAIL: refresh_current method not found.")

if __name__ == "__main__":
    test_phase_1()
    test_phase_2()
    test_phase_3()
    print("\n--- [STATIC TEST COMPLETE] ---")
