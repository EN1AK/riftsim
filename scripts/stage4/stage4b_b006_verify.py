# -*- coding: utf-8 -*-
"""B006 post-run spot checks (read-only)."""
import json, sqlite3
con = sqlite3.connect("workspace/rules_work.db")
con.row_factory = sqlite3.Row
out = {}

# task registry
out["task_4b_06"] = [dict(r) for r in con.execute(
    "SELECT * FROM processing_tasks WHERE task_id='task_4b_06'")]

# spot: a topic rule with applied 019 (R-TOPIC-EN-63 has 4), a pure interp CN rule, front rules
out["en63"] = [dict(r) for r in con.execute("""
    SELECT rule_id, status, needs_verification, length(official_interpretation) oi_len,
           substr(official_interpretation,1,200) oi_head
    FROM rules WHERE rule_id IN ('R-TOPIC-EN-63','R-TOPIC-CN-40','R-ER-FRONT','R-FAQ-FRONT','R-MISC-source_012')""")]

out["rec_en63"] = [dict(r) for r in con.execute(
    "SELECT * FROM reconciliations WHERE rule_id='R-TOPIC-EN-63'")]

out["chg_sample"] = [dict(r) for r in con.execute(
    "SELECT change_id, rule_id, substr(new_content,1,120) nc, modification_type, final_conclusion FROM changes WHERE change_id LIKE 'CHG-4B-T3-%' ORDER BY 1 LIMIT 3")]

# watch cards nv
out["watch_nv"] = [dict(r) for r in con.execute(
    "SELECT rule_id, needs_verification FROM rules WHERE rule_id IN ('R-CARD-OGN-131','R-CARD-OGN-251','R-CARD-UNL-097','R-CARD-UNL-177')")]

# every rule now has pcr or explicit NULL-canonical REC note? quick aggregate
out["rules_status"] = [dict(r) for r in con.execute(
    "SELECT status, COUNT(*) n FROM rules GROUP BY 1")]

# card 019 link details (SFD-111)
out["card_oi_check"] = [dict(r) for r in con.execute("""
    SELECT rule_id, length(official_interpretation) l FROM rules
    WHERE rule_id IN ('R-CARD-SFD-111','R-CARD-UNL-106','R-CARD-UNL-118','R-CARD-UNL-138','R-CARD-UNL-184','R-CARD-OGN-250','R-CARD-SFD-202','R-CARD-UNL-118a')""")]

print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
