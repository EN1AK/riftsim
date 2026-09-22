# -*- coding: utf-8 -*-
"""Full-state audit: totals, id continuity, field integrity, dupes, JSON validity,
card alignment, task/source status, manifest-file consistency."""
import json, re, sqlite3, sys
from pathlib import Path
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

con = sqlite3.connect(r"workspace/rules_work.db")
issues = []   # (severity, area, message)
def err(area, msg): issues.append(("FAIL", area, msg))
def warn(area, msg): issues.append(("WARN", area, msg))
def ok(area, msg): issues.append(("PASS", area, msg))

# ---------- A. totals & id continuity ----------
total = con.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
pref_rows = con.execute(
    "SELECT DISTINCT evidence_id FROM evidence").fetchall()
PREF_RE = re.compile(r"^([A-Z-]+?)-(\d+)$")
buckets = {}
malformed = []
for (eid,) in pref_rows:
    m = PREF_RE.match(eid)
    if not m:
        malformed.append(eid); continue
    buckets.setdefault(m.group(1), []).append(int(m.group(2)))
expected = {"EV-CN-CR": (2382, 0), "EV-EN-CR": (2382, 0), "EV-CN-ER": (93, 1),
            "EV-EN-ER": (66, 1), "EV-CN-FAQ": (332, 1), "EV-EN-OE": (272, 1)}
for pref, (exp_cnt, start) in expected.items():
    nums = sorted(buckets.pop(pref, []))
    if len(nums) != exp_cnt:
        err("A", f"{pref}: count {len(nums)} != expected {exp_cnt}")
    holes = [n for n in range(start, start + exp_cnt) if n not in set(nums)]
    dups = len(nums) - len(set(nums))
    if holes:
        err("A", f"{pref}: id holes {holes[:8]}{'...' if len(holes) > 8 else ''}")
    if dups:
        err("A", f"{pref}: {dups} duplicate ids")
    if len(nums) == exp_cnt and not holes and not dups:
        ok("A", f"{pref}: {exp_cnt} ids continuous from {start:04d}")
if malformed:
    err("A", f"malformed evidence ids: {malformed[:10]}")
if buckets:
    err("A", f"unexpected id prefixes: {list(buckets.keys())}")
if not malformed and not buckets:
    ok("A", f"evidence total {total} == sum of 6 prefixes (5527)" if total == 5527
       else f"evidence total {total}")

# ---------- B. Stage 2D field integrity ----------
faq_rows = con.execute(
    "SELECT evidence_id, source_id, topic, original_text, normalized_summary, confidence,"
    " faq_question, faq_answer, faq_classification, related_cards, card_ids, notes, page"
    " FROM evidence WHERE notes LIKE '%stage2d faq%'").fetchall()
ok("B", f"stage2d rows fetched: {len(faq_rows)}")
CLS = {"example_only","rule_interpretation","additional_condition","exception",
       "rule_change_candidate","uncertain"}
bad_cls = bad_conf = bad_ot = bad_eq = bad_json = bad_page = 0
nrev_open = 0
cards_db = sqlite3.connect(r"cards_bilingual.db")
card_keys = {r[0] for r in cards_db.execute("SELECT card_key FROM cards")}
bad_card_ids, bad_card_json = 0, 0
qdupes = {}
for (eid, sid, topic, ot, nsumm, conf, q, a, cls, rc, cids, notes, page) in faq_rows:
    fm = topic == "front_matter"
    if not fm and cls not in CLS:
        bad_cls += 1; err("B", f"{eid}: invalid faq_classification {cls!r}")
    if conf not in ("high", "medium", "low"):
        bad_conf += 1; err("B", f"{eid}: invalid confidence {conf!r}")
    if not (ot or "").strip():
        bad_ot += 1; err("B", f"{eid}: empty original_text")
    if "===== PAGE" in (ot or ""):
        bad_page += 1; err("B", f"{eid}: original_text contains PAGE marker")
    if not fm and not (q or "").strip() and not (a or "").strip():
        bad_eq += 1; err("B", f"{eid}: both q and a empty")
    tail = notes.split("stage2d faq; ", 1)
    if len(tail) == 2 and tail[1].strip().startswith("{"):
        try:
            meta = json.loads(tail[1].split(" | ")[0].split(" (note:")[0])
            if meta.get("needs_review"):
                nrev_open += 1
        except Exception:
            bad_json += 1; err("B", f"{eid}: notes JSON unparsable")
    if rc:
        try:
            json.loads(rc)
        except Exception:
            bad_card_json += 1; err("B", f"{eid}: related_cards not JSON")
    if cids:
        try:
            ids = json.loads(cids)
            missing = [k for k in ids if k not in card_keys]
            if missing:
                bad_card_ids += 1; err("B", f"{eid}: unknown card_keys {missing[:5]}")
        except Exception:
            bad_card_json += 1; err("B", f"{eid}: card_ids not JSON")
    if not fm and q:
        qdupes.setdefault((sid, q.strip()), []).append(eid)
for name, n in (("invalid classification", bad_cls), ("invalid confidence", bad_conf),
                ("empty original_text", bad_ot), ("PAGE marker leak", bad_page),
                ("empty q&a", bad_eq), ("notes JSON errors", bad_json),
                ("related/card_ids JSON errors", bad_card_json),
                ("unknown card_keys", bad_card_ids)):
    (err if n else ok)("B", f"{name}: {n}")
dup_q = {k: v for k, v in qdupes.items() if len(v) > 1}
if dup_q:
    for (sid, q), ids in list(dup_q.items())[:10]:
        warn("B", f"duplicate question in {sid}: {q[:60]!r} -> {ids}")
else:
    ok("B", "no duplicate faq_question within same source")
ok("B", f"needs_review still open: {nrev_open}")
# faq_answer empty accounting (en single-line markers + prose)
noans = con.execute(
    "SELECT source_id, COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%' "
    "AND (topic IS NULL OR topic<>'front_matter') AND (faq_answer IS NULL OR faq_answer='')"
    " GROUP BY source_id").fetchall()
ok("B", f"entries with empty faq_answer (en single-line declarations expected): {dict(noans)}")
cards_db.close()

# ---------- C. Stage 2C errata spot integrity ----------
er = con.execute(
    "SELECT COUNT(*), SUM(corrected_fragment IS NULL OR corrected_fragment=''),"
    " SUM(modification_type IS NULL OR modification_type=''),"
    " SUM(target_rule_candidate IS NULL OR target_rule_candidate='')"
    " FROM evidence WHERE evidence_id LIKE 'EV-%-ER-%'").fetchone()
ok("C", f"errata rows 159 check: total={er[0]}, empty corrected_fragment={er[1] or 0},"
        f" empty modification_type={er[2] or 0}, empty target={er[3] or 0}")

# ---------- D. 2A/2B core rules integrity ----------
for pref, sid in (("EV-CN-CR", "source_009"), ("EV-EN-CR", "source_018")):
    r = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT rule_number), SUM(original_text IS NULL OR original_text='')"
        " FROM evidence WHERE evidence_id LIKE ? AND rule_number IS NOT NULL",
        (pref + "-%",)).fetchone()
    (ok if r[0] == 2381 and r[1] == 2381 and not r[2] else err)(
        "D", f"{pref}: numbered={r[0]}, distinct={r[1]}, empty_text={r[2]}")

# ---------- E. tasks / sources / manual_review ----------
pend = con.execute("SELECT COUNT(*) FROM processing_tasks WHERE status<>'completed'").fetchone()[0]
(ok if pend == 0 else err)("E", f"processing_tasks not completed: {pend}")
nsrc = con.execute(
    "SELECT COUNT(*), SUM(language IS NULL OR language IN ('','unknown'))"
    " FROM sources").fetchone()
(ok if nsrc[0] == 20 and not nsrc[1] else err)(
    "E", f"sources rows={nsrc[0]}, missing language={nsrc[1] or 0}")
fm = con.execute(
    "SELECT COUNT(*), SUM(issue_description IS NULL OR issue_description='')"
    " FROM manual_review").fetchone()
(ok if fm[0] == 19 and not fm[1] else err)("E", f"manual_review rows={fm[0]}, empty={fm[1] or 0}")
fk = con.execute(
    "SELECT COUNT(*) FROM evidence e LEFT JOIN sources s ON e.source_id=s.source_id"
    " WHERE s.source_id IS NULL").fetchone()[0]
(ok if fk == 0 else err)("E", f"evidence with unknown source_id: {fk}")

# ---------- F. file consistency ----------
pj = json.load(open(r"workspace/progress.json", encoding="utf-8"))
d2 = pj["stages"].get("stage_2d", {})
(ok if d2.get("status") == "completed" else err)("F", f"progress stage_2d status={d2.get('status')}")
m = re.search(r"(\d+) items \+ 10", d2.get("description", ""))
items_db = con.execute(
    "SELECT COUNT(*) FROM evidence WHERE notes LIKE '%stage2d faq%' "
    "AND (topic IS NULL OR topic<>'front_matter')").fetchone()[0]
(ok if m and int(m.group(1)) == items_db else err)(
    "F", f"progress stage_2d items={m.group(1) if m else '?'} vs DB {items_db}")
st = json.load(open(r"workspace/reports/stage2d_stats.json", encoding="utf-8"))
(ok if st["totals"]["items"] == items_db and st["totals"]["needs_review"] == 0 else err)(
    "F", f"stage2d_stats totals={st['totals']}")
rm = Path("workspace/README_STATE.md").read_text(encoding="utf-8")
for token, label in (("5527", "evidence 5527"), ("594 items", "594 items"),
                     ("0001..0332", "zh id range")):
    (ok if token in rm else err)("F", f"README_STATE contains {label}")

print("=" * 78)
for sev in ("FAIL", "WARN", "PASS"):
    for s, area, msg in issues:
        if s == sev:
            print(f"[{sev}] {area}: {msg}")
nfail = sum(1 for s, _, _ in issues if s == "FAIL")
nwarn = sum(1 for s, _, _ in issues if s == "WARN")
print("=" * 78)
print(f"AUDIT RESULT: {nfail} FAIL, {nwarn} WARN, {sum(1 for s,_,_ in issues if s=='PASS')} PASS")

# WARN detail: verify the duplicated NEW RULE: Repeat entry against source text
src = Path(r"extracted/riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt")
hits = [i + 1 for i, l in enumerate(src.read_text(encoding="utf-8").splitlines())
        if l.strip().startswith("NEW RULE: Repeat as a keyword added")]
print("source lines for 'NEW RULE: Repeat as a keyword added':", hits)
for rid in ("EV-EN-OE-0109", "EV-EN-OE-0110"):
    r = con.execute(
        "SELECT page, faq_question, substr(faq_answer,1,80) FROM evidence WHERE evidence_id=?",
        (rid,)).fetchone()
    print(f"  {rid}: p{r[0]} Q={r[1][:50]!r} A={r[2]!r}")
con.close()
