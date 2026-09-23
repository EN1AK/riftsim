import sqlite3
import os

# Create database file
db_path = "c:/Users/Mortis/Desktop/Workspace/riftsim/workspace/rules_work.db"

# Ensure directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tables as specified in the prompt
cursor.execute('''CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    source_document TEXT,
    source_type TEXT,
    language TEXT,
    version TEXT,
    date TEXT,
    effective_date TEXT,
    page_count INTEGER,
    supersedes TEXT,
    possible_counterpart TEXT,
    date_confidence TEXT,
    version_confidence TEXT,
    notes TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS processing_tasks (
    task_id TEXT PRIMARY KEY,
    source_id TEXT,
    page_start INTEGER,
    page_end INTEGER,
    section TEXT,
    status TEXT,
    assigned_role TEXT,
    notes TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    rule_id_candidate TEXT,
    topic TEXT,
    source_id TEXT,
    source_type TEXT,
    source_language TEXT,
    source_document TEXT,
    version TEXT,
    date TEXT,
    page INTEGER,
    section TEXT,
    heading TEXT,
    rule_number TEXT,
    original_text TEXT,
    normalized_summary TEXT,
    applicable_object TEXT,
    trigger TEXT,
    precondition TEXT,
    effect TEXT,
    restriction TEXT,
    exception TEXT,
    example TEXT,
    confidence TEXT,
    notes TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS rules (
    rule_id TEXT PRIMARY KEY,
    topic TEXT,
    proposed_canonical_rule TEXT,
    applicable_object TEXT,
    trigger TEXT,
    precondition TEXT,
    effect TEXT,
    restriction TEXT,
    exception TEXT,
    official_interpretation TEXT,
    derived_interpretation TEXT,
    example TEXT,
    status TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS rule_evidence (
    rule_id TEXT,
    evidence_id TEXT,
    relationship TEXT,
    confidence TEXT,
    notes TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS alignments (
    alignment_id TEXT PRIMARY KEY,
    evidence_a TEXT,
    evidence_b TEXT,
    relation TEXT,
    confidence TEXT,
    version_relation TEXT,
    notes TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS reconciliations (
    reconciliation_id TEXT PRIMARY KEY,
    rule_id TEXT,
    source_id TEXT,
    original_fragment TEXT,
    corrected_fragment TEXT,
    modification_type TEXT,
    effective_scope TEXT,
    status TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS changes (
    change_id TEXT PRIMARY KEY,
    rule_id TEXT,
    original_content TEXT,
    new_content TEXT,
    source_type TEXT,
    source_language TEXT,
    source_document TEXT,
    version TEXT,
    date TEXT,
    modification_type TEXT,
    reason TEXT,
    final_conclusion TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS conflicts (
    conflict_id TEXT PRIMARY KEY,
    rule_id TEXT,
    evidence_a TEXT,
    evidence_b TEXT,
    conflict_type TEXT,
    resolution_status TEXT,
    notes TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS manual_review (
    item_id TEXT PRIMARY KEY,
    rule_id TEXT,
    issue_description TEXT,
    source_a TEXT,
    source_b TEXT,
    conflicting_points TEXT,
    possible_explanation TEXT,
    cannot_auto_resolve_reason TEXT
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS verification (
    verification_id TEXT PRIMARY KEY,
    rule_id TEXT,
    status TEXT,
    notes TEXT
)''')

conn.commit()
conn.close()

print("Database initialized successfully")