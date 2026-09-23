# -*- coding: utf-8 -*-
"""Stage 4B batch 006 (task_4b_06): reconcile 88 pending rules
(81 R-TOPIC + 5 R-MISC + R-ER-FRONT + R-FAQ-FRONT) and adjudicate the
remaining 128 faq:rule_change_candidate (RCC) links.

Authority adjudication (Group-C topology, MR-2D-0009/0010/0013, B005 scope):
  - source_005 (zh FAQ 2026-04-15, pre-core)         -> incorporated-check
    * EV-CN-FAQ-0055 (735.1.c revised) -> INCORPORATED into 2026-07 core 809.1.c
      (EV-CN-CR-2140; MR-2D-0007 + B005 precedent). CHG row, NOT applied.
  - source_012/014/016 (EN patch notes, transitional pre-2026-07-core)
    -> transitional; authority superseded by 2026-07 core release; NOT applied;
       recorded in REC; per-item incorporation check deferred to Stage 5.
  - source_019 (Vendetta Patch Notes, eff 2026-07-24, post-core)
    -> authoritative side: APPLY as official changes; CHG rows per link; nv=true.

Also fold-in: MR-2D-0005 pending_zh_text_update watch (4 cards:
R-CARD-OGN-131 / OGN-251 / UNL-097 / UNL-177) -> REC watch rows, nv=true.

Idempotent: DELETE all REC-4B-T3-% / CHG-4B-T3-% rows, recompute, re-insert.
Run exactly once per batch; verify stats from DB afterwards (sandbox-retry
incident of B002/B004/B005: printed run-stats can be lost on retries).
"""
import json, sqlite3, datetime

DB = "workspace/rules_work.db"
NOW = "2026-09-22"

JUDGE = {"source_001", "source_006", "source_008"}          # judge-community tier (MR-2D-0013)
TRANSITIONAL = {"source_012", "source_014", "source_016"}   # pre-2026-07-core EN patch notes
APPLY = {"source_019"}                                      # post-core Vendetta patch notes
S019_DOC = "08_2026-07-17_Vendetta_Patch_Notes.pdf"
S005_DOC = "05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.pdf"
WATCH = {  # MR-2D-0005 fold-in
    "R-CARD-OGN-131": "沙丘亚龙 OGN-131",
    "R-CARD-OGN-251": "金克丝-暴走萝莉 OGN-251",
    "R-CARD-UNL-097": "均衡门徒 UNL-097",
    "R-CARD-UNL-177": "艾翁-万物之友 UNL-177",
}

def tier(src):
    return "judge-community" if src in JUDGE else "official"

def fmt_attach(e):
    """[eid | src | tier | class]\nQ: ...\nA: ...  (q NULL -> answer/original only)"""
    head = "[{} | {} | {} | {}]".format(
        e["evidence_id"], e["source_id"], tier(e["source_id"]), e["faq_classification"])
    q, a = e["faq_question"], e["faq_answer"]
    if q and a:
        body = "Q: {}\nA: {}".format(q, a)
    elif q:
        body = q
    else:
        body = a or e["original_text"] or ""
    return head + "\n" + body

def fmt_applied(e):
    head = "[{} | {} | official | rule_change_candidate | APPLIED post-core official change]".format(
        e["evidence_id"], e["source_id"])
    q, a = e["faq_question"], e["faq_answer"]
    body = ("Q: {}\nA: {}".format(q, a) if q and a else (q or a or e["original_text"] or ""))
    return head + "\n" + body

def short(txt, n=110):
    t = (txt or "").replace("\n", " ").strip()
    return t[:n] + ("…" if len(t) > n else "")

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

# ---- idempotency wipe ----
cur.execute("DELETE FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T3-%'")
cur.execute("DELETE FROM changes WHERE change_id LIKE 'CHG-4B-T3-%'")

stats = {"rules_reconciled": 0, "interp_attached": 0, "rcc_transitional": 0,
         "rcc_applied_019": 0, "rcc_incorporated": 0, "chg_rows": 0,
         "rec_rows": 0, "nv_true": 0, "nv_false": 0, "watch_cards": 0,
         "card_rcc_rules": 0, "errors": [], "warnings": []}

chg_n = 0
def add_chg(rule_id, e, mod_type, reason, conclusion, lang="en", doc=S019_DOC,
            stype="official_explanation", date="2026-07-24"):
    global chg_n
    chg_n += 1
    q, a = e["faq_question"], e["faq_answer"]
    newc = (q + ("\n" + a if a else "")) if q else (a or e["original_text"] or "")
    cur.execute("""INSERT INTO changes(change_id, rule_id, original_content, new_content,
        source_type, source_language, source_document, version, date,
        modification_type, reason, final_conclusion)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("CHG-4B-T3-%04d" % chg_n, rule_id, None, newc, stype, lang, doc,
         None, date, mod_type, reason, conclusion))
    stats["chg_rows"] += 1

def get_link_evs(rule_id, rel_classes=None):
    sql = """SELECT re.evidence_id, re.relationship, e.source_id, e.faq_classification,
                    e.faq_question, e.faq_answer, e.original_text, e.topic
             FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
             WHERE re.rule_id=?"""
    rows = [dict(r) for r in cur.execute(sql, (rule_id,))]
    if rel_classes:
        rows = [r for r in rows if r["relationship"] in rel_classes]
    return rows

# ============ PART A: 88 pending rules ============
pending = [r["rule_id"] for r in cur.execute(
    "SELECT rule_id FROM rules WHERE status='pending_reconciliation' ORDER BY rule_id")]

for rid in pending:
    links = get_link_evs(rid)
    interp = sorted([l for l in links if l["relationship"] == "faq:rule_interpretation"],
                    key=lambda x: x["evidence_id"])
    rcc = sorted([l for l in links if l["relationship"] == "faq:rule_change_candidate"],
                 key=lambda x: x["evidence_id"])
    front = [l for l in links if l["relationship"] == "front_matter"]

    oi_parts = [fmt_attach(l) for l in interp]
    applied = [l for l in rcc if l["source_id"] in APPLY]
    for l in applied:
        oi_parts.append(fmt_applied(l))
        add_chg(rid, l, "new_rule_addition",
                "post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE/SYSTEM; "
                "authoritative side per MR-2D-0010 authority topology + 4B-B005 scope decision",
                "applied as official change (recorded verbatim on rule); Stage 5 verification required")
        stats["rcc_applied_019"] += 1

    rec_notes = []
    inc = [l for l in rcc if l["source_id"] == "source_005"]
    for l in inc:
        add_chg(rid, l, "other",
                "FAQ(source_005) declared 735.1.c revised text ('预时之门' 法盾费用语义); "
                "absorbed into 2026-07 core rules as 809.1.c (EV-CN-CR-2140; MR-2D-0007 + B005 precedent)",
                "incorporated into 2026-07 core rules; recorded, not applied",
                lang="zh", doc=S005_DOC, stype="faq", date="2026-04-15")
        rec_notes.append("{} INCORPORATED into 2026-07 core 809.1.c (EV-CN-CR-2140): {}".format(
            l["evidence_id"], short(l["faq_question"])))
        stats["rcc_incorporated"] += 1

    trs = [l for l in rcc if l["source_id"] in TRANSITIONAL]
    for l in trs:
        rec_notes.append("{} {} NOT applied (transitional pre-2026-07-core patch note; authority "
                         "superseded by 2026-07 core release per MR-2D-0009/0010; incorporation "
                         "check deferred to Stage 5): {}".format(
                             l["evidence_id"], l["source_id"], short(l["faq_question"] or l["faq_answer"])))
        stats["rcc_transitional"] += 1

    nv = "true" if rcc else "false"
    oi = "\n\n".join(oi_parts) if oi_parts else None
    cur.execute("""UPDATE rules SET official_interpretation=?, status='reconciled',
                   needs_verification=? WHERE rule_id=?""", (oi, nv, rid))

    kind = ("front_matter" if front and not (interp or rcc) else "faq_topic_bucket")
    if kind == "front_matter":
        frag = "front-matter bucket ({} rows: {}); no rule text; canonical stays NULL by design".format(
            len(front), ", ".join(sorted({l["evidence_id"] for l in front})))
        scope = "front_matter"
    else:
        frag = ("faq attach: rule_interpretation={} rule_change_candidate={} ({}: 019 applied, "
                "{}: transitional not-applied, {}: incorporated); FAQ topic/misc aggregation bucket: "
                "no own rulebook/errata text, canonical stays NULL".format(
                    len(interp), len(rcc), len(applied), len(trs), len(inc)))
        if rec_notes:
            frag += " || " + " ; ".join(rec_notes)
        scope = "faq_attach" + (";rcc_adjudication" if rcc else "")
    cur.execute("""INSERT INTO reconciliations(reconciliation_id, rule_id, source_id,
        original_fragment, corrected_fragment, modification_type, effective_scope, status)
        VALUES(?,?,?,?,?,?,?,?)""",
        ("REC-4B-T3-" + rid, rid,
         "+".join(sorted({l["source_id"] for l in links})) or "none",
         frag, None, "other" if applied else "none", scope, "reconciled_tier3"))
    stats["rec_rows"] += 1
    stats["rules_reconciled"] += 1
    stats["interp_attached"] += len(interp)
    stats["nv_true" if nv == "true" else "nv_false"] += 1

# ============ PART B: 11 RCC links on already-reconciled R-CARD rules ============
card_links = [dict(r) for r in cur.execute("""
    SELECT re.rule_id, re.evidence_id, e.source_id, e.faq_question, e.faq_answer,
           e.original_text, e.faq_classification
    FROM rule_evidence re JOIN evidence e ON e.evidence_id=re.evidence_id
    WHERE re.relationship='faq:rule_change_candidate'
      AND re.rule_id LIKE 'R-CARD%' ORDER BY re.rule_id, re.evidence_id""")]
by_card = {}
for l in card_links:
    by_card.setdefault(l["rule_id"], []).append(l)

for rid, links in by_card.items():
    notes, applied = [], []
    for l in links:
        if l["source_id"] in APPLY:
            applied.append(l)
            add_chg(rid, l, "new_rule_addition",
                    "post-core official patch notes (Vendetta, eff 2026-07-24) declare NEW RULE "
                    "affecting this card's interaction space; authoritative side per MR-2D-0010 + B005 scope",
                    "applied as official change (recorded in changes table; card canonical unchanged "
                    "-- errata text remains canonical); Stage 5 verification required")
            notes.append("{} APPLIED (post-core official change): {}".format(
                l["evidence_id"], short(l["faq_question"])))
            stats["rcc_applied_019"] += 1
        else:
            notes.append("{} {} NOT applied (transitional pre-2026-07-core): {}".format(
                l["evidence_id"], l["source_id"], short(l["faq_question"] or l["faq_answer"])))
            stats["rcc_transitional"] += 1
    # append applied text onto existing official_interpretation (B002/B004 attach intact)
    if applied:
        row = cur.execute("SELECT official_interpretation FROM rules WHERE rule_id=?", (rid,)).fetchone()
        cur_oi = row["official_interpretation"] or ""
        extra = "\n\n".join(fmt_applied(l) for l in applied)
        new_oi = (cur_oi + "\n\n" + extra) if cur_oi else extra
        cur.execute("UPDATE rules SET official_interpretation=? WHERE rule_id=?", (new_oi, rid))
    cur.execute("UPDATE rules SET needs_verification='true' WHERE rule_id=?", (rid,))
    cur.execute("""INSERT INTO reconciliations(reconciliation_id, rule_id, source_id,
        original_fragment, corrected_fragment, modification_type, effective_scope, status)
        VALUES(?,?,?,?,?,?,?,?)""",
        ("REC-4B-T3-" + rid, rid, "+".join(sorted({l["source_id"] for l in links})),
         "rcc adjudication on already-reconciled card rule (B002/B004 canonical untouched): "
         + " ; ".join(notes), None, "other" if applied else "none",
         "rcc_adjudication", "reconciled_tier3"))
    stats["rec_rows"] += 1
    stats["card_rcc_rules"] += 1

# ============ PART C: MR-2D-0005 watch fold-in ============
for rid, cname in WATCH.items():
    row = cur.execute("SELECT * FROM rules WHERE rule_id=?", (rid,)).fetchone()
    if not row:
        stats["errors"].append("watch card missing: " + rid)
        continue
    has260 = cur.execute("""SELECT COUNT(*) c FROM rule_evidence
        WHERE rule_id=? AND evidence_id='EV-CN-FAQ-0260'""", (rid,)).fetchone()["c"]
    note = ("MR-2D-0005 watch fold-in ({}): zh/en semantic divergence (conditional-clause position "
            "-> condition check timing trigger-vs-resolution); current ruling per zh designer FAQ "
            "source_008 sec.4 (EV-CN-FAQ-0260链接={}), EN text = authority reference; "
            "pending_zh_text_update watch pending future zh errata; needs_verification=true".format(
                cname, "present" if has260 else "ABSENT (card named in MR issue text; sec.4 doc-level analysis)"))
    if not has260:
        stats["warnings"].append("EV-CN-FAQ-0260 not linked to " + rid)
    cur.execute("UPDATE rules SET needs_verification='true' WHERE rule_id=?", (rid,))
    cur.execute("""INSERT INTO reconciliations(reconciliation_id, rule_id, source_id,
        original_fragment, corrected_fragment, modification_type, effective_scope, status)
        VALUES(?,?,?,?,?,?,?,?)""",
        ("REC-4B-T3-" + rid, rid, "source_008", note, None, "none",
         "mr2d0005_watch_fold_in", "reconciled_tier3"))
    stats["rec_rows"] += 1
    stats["watch_cards"] += 1

con.commit()

# ---- post-run DB verification ----
v = {}
v["pending_left"] = cur.execute(
    "SELECT COUNT(*) FROM rules WHERE status='pending_reconciliation'").fetchone()[0]
v["reconciled_total"] = cur.execute(
    "SELECT COUNT(*) FROM rules WHERE status='reconciled'").fetchone()[0]
v["rec_t3"] = cur.execute(
    "SELECT COUNT(*) FROM reconciliations WHERE reconciliation_id LIKE 'REC-4B-T3-%'").fetchone()[0]
v["chg_t3"] = cur.execute(
    "SELECT COUNT(*) FROM changes WHERE change_id LIKE 'CHG-4B-T3-%'").fetchone()[0]
v["rec_total"] = cur.execute("SELECT COUNT(*) FROM reconciliations").fetchone()[0]
v["chg_total"] = cur.execute("SELECT COUNT(*) FROM changes").fetchone()[0]
v["nv_true_total"] = cur.execute(
    "SELECT COUNT(*) FROM rules WHERE needs_verification='true'").fetchone()[0]
v["rcc_links_remaining_on_pending"] = cur.execute("""
    SELECT COUNT(*) FROM rule_evidence WHERE relationship='faq:rule_change_candidate'
      AND rule_id IN (SELECT rule_id FROM rules WHERE status='pending_reconciliation')""").fetchone()[0]
stats["verify"] = v

ckpt = {"batch": "4B-B006", "task": "task_4b_06", "date": NOW, "stats": stats}
with open("workspace/checkpoints/stage4b_b006_checkpoint.json", "w", encoding="utf-8") as f:
    json.dump(ckpt, f, ensure_ascii=False, indent=1)
print(json.dumps(ckpt, ensure_ascii=False, indent=1))
