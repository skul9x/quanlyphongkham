import os
import sys

def cleanup_old_files():
    """
    Removes obsolete Tkinter-based files from the project directory
    to finalize the migration to PySide6.
    """
    files_to_remove = [
        # Main entry points and controllers
        "main.py",
        "app.py",
        
        # Old Logic/Action modules (Logic moved to UI classes or Worker)
        "patient_actions.py",
        "medicine_actions.py",
        "stats_actions.py",
        "patient_logic.py",
        "theme_manager.py", # Replaced by theme_manager_pyside.py
        
        # Old UI Modules (Tabs)
        "ui_patient_tab.py",
        "ui_patient_components.py",
        "ui_medicine_tab.py",
        "ui_medicine_components.py",
        "ui_stats_tab.py",
        "ui_stats_components.py",
        "ui_help_tab.py",
        
        # Old UI Windows/Dialogs
        "ui_add_patient_window.py",
        "ui_add_visit_window.py",
        "ui_edit_visit_window.py",
        "ui_edit_diagnosis_window.py",
        "ui_prescription_window.py",
        "ui_dose_calculator.py",
    ]

    print("--- Starting Cleanup of Obsolete Tkinter Files ---")
    
    deleted_count = 0
    not_found_count = 0
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"[DELETED] {file_name}")
                deleted_count += 1
            except OSError as e:
                print(f"[ERROR] Could not delete {file_name}: {e}")
        else:
            # print(f"[NOT FOUND] {file_name} (Already removed?)")
            not_found_count += 1

    print("-" * 40)
    print(f"Cleanup Complete.")
    print(f"Files deleted: {deleted_count}")
    print(f"Files not found: {not_found_count}")
    print("-" * 40)
    print("You can now run the application using: python main_pyside.py")

if __name__ == "__main__":
    confirmation = input("This will DELETE the old Tkinter source files. Are you sure? (y/n): ")
    if confirmation.lower() == 'y':
        cleanup_old_files()
    else:
        print("Cleanup cancelled.")