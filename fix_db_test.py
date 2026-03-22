import sqlite3
import database

# Need to change `update_visit_details_db`
# It should still update `patients.weight` and `patients.medical_history` and `patients.diagnosis`.
# AND it should ALSO:
# 1. Parse the new `medical_history` text.
# 2. Get the latest `prescriptions_header` for the patient.
# 3. If there are medicines, update/replace the prescription details.

