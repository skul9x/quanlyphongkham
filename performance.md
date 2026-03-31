# Python Performance Review Report

## 1. Executive Summary
- The largest risks are concentrated in database write amplification and sync architecture, not raw Python arithmetic.
- The code has several N+1 patterns and per-row transaction patterns that will degrade sharply as data grows.
- UI responsiveness risks are mostly from repeated full-list transforms and expensive per-keystroke normalization.
- Estimated impact if top fixes are applied:
- Bulk cloud restore/import throughput: 5x-30x faster (single transaction + batch insert/upsert patterns).
- Sync catch-up latency under network issues: 2x-10x lower tail latency (remove queue head-of-line blocking).
- Search/list/filter responsiveness on large medicine/patient sets: 2x-5x faster perceived UI response.

## 2. Critical Issues

### C1. Cloud Restore Uses Per-Row DB Connections and Commits
- Description:
- Full restore loops over cloud rows and calls insert helpers that each open a new SQLite connection and commit once per row.
- Evidence:
- [sync_manager.py](sync_manager.py#L300), [sync_manager.py](sync_manager.py#L312), [sync_manager.py](sync_manager.py#L324), [sync_manager.py](sync_manager.py#L336)
- [database.py](database.py#L1327), [database.py](database.py#L1361), [database.py](database.py#L1388), [database.py](database.py#L1415)
- Root cause:
- Row-by-row I/O with connection setup and transaction commit inside each helper.
- Performance impact:
- Extremely high disk sync overhead and lock churn; restore time scales poorly with data volume.
- Recommended fix:
- Use one connection + explicit transaction for each table batch (or one global transaction for restore), and `executemany` where possible.
- Code example (before/after):

```python
# Before
for med in medicines:
    database.insert_medicine_from_cloud(med)  # opens/closes connection each row
```

```python
# After
def insert_medicines_from_cloud_bulk(rows):
    conn = _get_db_connection()
    try:
        c = conn.cursor()
        c.execute("BEGIN")
        c.executemany(
            """
            INSERT OR REPLACE INTO medicines (id, name, packing_spec, price, stock_quantity, min_stock_level)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    r.get("id"), r.get("name"), r.get("packing_spec"), r.get("price"),
                    r.get("stock_quantity", 0), r.get("min_stock_level", 5),
                )
                for r in rows
            ],
        )
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### C2. Sync Worker Has Head-of-Line Blocking on Retry Sleep
- Description:
- A single worker thread retries failed tasks with blocking `sleep(1/3/5)` inside the processing loop.
- Evidence:
- [sync_manager.py](sync_manager.py#L66), [sync_manager.py](sync_manager.py#L111)
- Root cause:
- Retries are in-band with queue processing, so one failing record stalls all subsequent tasks.
- Performance impact:
- Severe backlog growth and delayed eventual consistency during network instability.
- Recommended fix:
- Decouple retries from the main queue: requeue failed tasks with `next_retry_at` timestamps, or use a secondary delayed queue.
- Code example (before/after):

```python
# Before
for attempt in range(max_retries):
    try:
        do_sync()
        break
    except Exception:
        time.sleep(retry_delays[attempt])
```

```python
# After (non-blocking retry)
try:
    do_sync()
except Exception:
    task["retry_count"] = task.get("retry_count", 0) + 1
    if task["retry_count"] <= 3:
        task["next_retry_at"] = time.time() + backoff(task["retry_count"])
        delayed_queue.put(task)  # main worker continues processing other tasks
```

### C3. Bulk Import Path Executes Per-Row Duplicate Check + Insert
- Description:
- Excel import checks existence and inserts one row at a time through DB functions that each create connections and trigger sync.
- Evidence:
- [ui_medicine_pyside.py](ui_medicine_pyside.py#L598)
- [database.py](database.py#L488), [database.py](database.py#L523)
- Root cause:
- N round-trips to DB and N sync enqueue operations for large spreadsheets.
- Performance impact:
- Import time grows superlinearly in practice due to repetitive overhead and sync queue pressure.
- Recommended fix:
- Parse all rows first, fetch existing names in one query, insert remaining rows in one transaction, then optionally bulk sync.
- Code example (before/after):

```python
# Before
for r in rows:
    if not database.get_medicine_by_name_db(name):
        database.add_medicine_db(name, spec, price)
```

```python
# After
existing = set(get_all_medicine_names_lower())
new_rows = [(n, s, p, 0, 5) for (n, s, p) in parsed if n.lower() not in existing]
bulk_insert_medicines(new_rows)  # one transaction
bulk_queue_sync_for_new_medicines(new_rows)
```

## 3. Major Issues

### M1. N+1 Query in Incremental Sync for Patients
- Description:
- Missing cloud IDs are found in set math, but each patient is fetched individually by ID before queueing.
- Evidence:
- [sync_manager.py](sync_manager.py#L434)
- Root cause:
- Per-ID query loop (`get_patient_by_id`) instead of single `IN (...)` query.
- Performance impact:
- O(N) DB round-trips for N missing patients, costly on startup sync.
- Recommended fix:
- Add `get_patients_by_ids(ids)` and queue in chunks.
- Trade-off:
- Slightly larger transient memory, much lower DB overhead.

### M2. N+1 Query in Prescription History Retrieval
- Description:
- Header rows are loaded, then details are queried separately per header.
- Evidence:
- [database.py](database.py#L1222)
- Root cause:
- Loop with nested detail query.
- Performance impact:
- Slow history rendering when patients have many prescriptions.
- Recommended fix:
- Fetch all details in one query using `WHERE prescription_header_id IN (...)`, then group in Python.

### M3. Re-syncing Entire Prescription Details on Append
- Description:
- After appending items to one prescription, code fetches all details for that header and syncs all of them again.
- Evidence:
- [database.py](database.py#L1179)
- Root cause:
- Full header detail resync for incremental updates.
- Performance impact:
- Redundant network payload; repeated appends can behave close to O(n^2) transferred rows.
- Recommended fix:
- Sync only newly inserted details (track inserted row IDs) plus header total update.

### M4. Query Patterns Defeat Indexes (`strftime`, `datetime`, leading `%` LIKE)
- Description:
- Several queries apply functions to indexed columns or use leading wildcard searches.
- Evidence:
- [database.py](database.py#L362), [database.py](database.py#L399), [database.py](database.py#L684), [database.py](database.py#L696), [database.py](database.py#L708)
- Root cause:
- Non-sargable predicates in SQLite.
- Performance impact:
- Table scans and temp sorting under growth.
- Recommended fix:
- Prefer range filtering using raw timestamp boundaries.
- Example: replace `strftime('%Y-%m', created_at)=?` with `created_at >= ? AND created_at < ?`.
- Add indexes:
- `patients(created_at)` already exists, but add `prescriptions_header(patient_id, prescription_date)`.
- Add `prescription_details(prescription_header_id)` and `prescription_details(medicine_id)` if missing.

### M5. UI Filter Performs Repeated Diacritic Normalization Per Keystroke
- Description:
- Medicine filter recomputes normalized names for every item on every keypress.
- Evidence:
- [ui_medicine_pyside.py](ui_medicine_pyside.py#L364)
- Root cause:
- No cached normalized field in memory.
- Performance impact:
- CPU spikes and jank with larger catalogs.
- Recommended fix:
- Cache `name_norm` once when data is loaded; debounce input to 150-250 ms.

### M6. Heavy Console Logging in High-Frequency Worker Path
- Description:
- Worker prints start/success/result/finish for every task.
- Evidence:
- [worker.py](worker.py#L26), [worker.py](worker.py#L30), [worker.py](worker.py#L40), [worker.py](worker.py#L49)
- Root cause:
- Verbose stdout logging in hot path.
- Performance impact:
- Significant overhead during bulk operations; noisy logs can become I/O bottleneck.
- Recommended fix:
- Replace with leveled logging and disable debug logs in production.

### M7. Duplicate Signal Connection Causes Redundant Work
- Description:
- Same slot connected twice in stats time-data fetch.
- Evidence:
- [ui_stats_pyside.py](ui_stats_pyside.py#L239)
- Root cause:
- Duplicate `worker.signals.result.connect(on_loaded)` line.
- Performance impact:
- Callback runs twice; duplicate UI updates and possible duplicate data loads.
- Recommended fix:
- Remove duplicate connection.

### M8. Startup Sync Pulls Full ID Sets Into Memory
- Description:
- Cloud and local IDs are materialized as sets before diff.
- Evidence:
- [sync_manager.py](sync_manager.py#L400), [sync_manager.py](sync_manager.py#L403), [sync_manager.py](sync_manager.py#L417)
- Root cause:
- Full snapshot compare strategy.
- Performance impact:
- Memory and latency spikes with large datasets.
- Recommended fix:
- Paginate cloud IDs and process diffs in chunks.

## 4. Minor Improvements
- Use `UNION ALL` instead of `UNION` in month/year source query if semantic duplicates are acceptable before final `DISTINCT` strategy review.
- Evidence: [database.py](database.py#L684)
- In medicine tree rendering, avoid repeated `dict(med)` conversions in tight loops by normalizing rows once at load.
- Evidence: [ui_medicine_pyside.py](ui_medicine_pyside.py#L304), [ui_medicine_pyside.py](ui_medicine_pyside.py#L374)
- Avoid repeated `datetime.strptime` in formatting loops when source format is already bounded and can be preformatted at DB layer or cached.
- Evidence: [ui_stats_pyside.py](ui_stats_pyside.py#L196), [ui_stats_pyside.py](ui_stats_pyside.py#L379)
- Consider lowering `QThreadPool` max thread count from 8 for this workload if disk-bound contention appears.
- Evidence: [ui_stats_pyside.py](ui_stats_pyside.py#L18)

## 5. Python Language-Level Optimizations
- Generators vs lists:
- Replace intermediate list creation where only aggregation is needed.

```python
# Before
total = sum([r[1] for r in rows if isinstance(r[1], (int, float))])

# After
total = sum(r[1] for r in rows if isinstance(r[1], (int, float)))
```

- Efficient data structures:
- Keep precomputed dictionaries/sets for repeated membership checks (already used in several places, good pattern). Extend this to medicine-name checks in import and filter caches.
- Loop optimization:
- Cache function references in hot loops if profiling confirms hotspots, for example `norm = utils.remove_diacritics` then call `norm(...)`.
- Avoid repeated `dict(row)` conversions by returning dict rows once from DB APIs where practical.

## 6. Concurrency & Parallelism
- Threading vs multiprocessing:
- Current app is primarily I/O-bound (SQLite, network, UI), so threading is appropriate; multiprocessing is unlikely to help and may complicate IPC/state.
- Asyncio improvements:
- No asyncio currently, which is fine for PySide architecture.
- Main concurrency improvements should focus on:
- Non-blocking sync retries (critical).
- Bounded queues/backpressure for sync tasks to prevent unbounded memory growth.
- Worker prioritization (UI-critical tasks over bulk sync tasks).

## 7. Memory Optimization
- Allocation reduction:
- Avoid loading entire large tables into memory where not necessary (`get_all_medicines_db` used by several UIs).
- Introduce pagination/virtualization for large medicine catalogs and stats views.
- Leak prevention:
- Worker tracking set is a good safeguard.
- Ensure all workers always connect `finished` to cleanup; keep this pattern consistent.
- Object churn:
- Repeated `dict(row)` in hot paths creates avoidable churn; normalize once at API boundary.

## 8. I/O Performance
- File operations:
- `drugs.json` load/save is straightforward and small; low risk.
- High-risk I/O is SQLite commit frequency during bulk operations.
- Logging efficiency:
- Replace frequent `print` with `logging` and handler levels.
- For production, route debug logs to rotating file and disable debug level by default.

## 9. Database Optimization
- Query improvements:
- Convert time filters from `strftime` wrappers to range predicates.
- Replace N+1 retrieval in prescription history with batched detail query.
- Add bulk insert/update APIs for cloud restore and Excel import.
- Index recommendations:
- Add if missing:
- `CREATE INDEX IF NOT EXISTS idx_ph_patient_date ON prescriptions_header(patient_id, prescription_date);`
- `CREATE INDEX IF NOT EXISTS idx_pd_header ON prescription_details(prescription_header_id);`
- `CREATE INDEX IF NOT EXISTS idx_pd_medicine ON prescription_details(medicine_id);`
- Validate with `EXPLAIN QUERY PLAN` for top queries.

## 10. Startup Performance
- Import optimization:
- Startup path is already improved with lazy-loaded tabs.
- Keep heavy modules imported lazily in non-critical paths (good existing pattern for splash import).
- Lazy initialization:
- Consider delaying sync manager startup until after first frame render if startup UX is still slow in offline scenarios.
- Minimize blocking DB/network checks during startup sequence.

## 11. Recommended Profiling Tools
- `cProfile`: End-to-end function-level CPU profiles for startup, restore, and import flows.
- `line_profiler`: Validate hotspot loops (`apply_filters`, stats format loops).
- `memory_profiler`: Detect transient spikes during cloud restore and set-diff sync.
- `tracemalloc`: Identify allocation hotspots from repeated row-to-dict conversions.
- `py-spy`: Low-overhead sampling in production-like runs.
- `Scalene`: Combined CPU/memory profiles to separate Python vs native cost.

## 12. Quick Wins
- Remove duplicate signal connection in stats loader ([ui_stats_pyside.py](ui_stats_pyside.py#L239)).
- Replace list-based `sum([...])` with generator forms in hot code paths.
- Cache normalized medicine names once after loading data; use in search filter.
- Change prescription append sync to only sync newly added details.
- Gate worker/debug `print` logs behind a debug flag.
- Add missing prescription indexes and validate query plans.

---

### Suggested Implementation Order
1. Bulk DB APIs for cloud restore/import (highest throughput gain).
2. Sync retry architecture update (eliminate queue head-of-line blocking).
3. N+1 removal in prescription retrieval and incremental sync fetch.
4. Query/index rewrite for time-range filters.
5. UI filter caching/debounce and logging reduction.
