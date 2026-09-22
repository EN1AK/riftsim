import sqlite3
DB = r"c:\Users\Mortis\Desktop\Workspace\riftsim\workspace\rules_work.db"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("""UPDATE processing_tasks SET status='completed',
             notes='Stage 3 closeout done 2026-09-21: MR-2D-0004/0005/0010 closed with findings; validation passed (rule_evidence_unpaired=0, errata_unresolved=0, faq_oe_untagged=0, dup_pairs=0); Stage 3 complete: 2382 AL-CR + 63 AL-ER alignments; 604 FAQ/OE + 33 errata/zh-only/NA rows explicitly unmatched-tagged; 161 MR-3-CR translation_difference flagged for Stage 4/5'
             WHERE task_id='task_3_05'""")
conn.commit()
c.execute("SELECT COUNT(*) FROM processing_tasks WHERE status NOT IN ('completed') AND task_id LIKE 'task_3_%'")
print("stage3 open tasks:", c.fetchone()[0])
conn.close()
