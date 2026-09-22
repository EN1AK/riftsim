# -*- coding: utf-8 -*-
"""Stage 2D — FAQ / Ruling / Official Explanation Evidence Extraction.

Parses 10 sources (6 zh FAQ + 4 en official_explanation patch notes) from
repo-root `extracted/`, extracts per-item FAQ/OE entries and writes
unified-schema evidence rows (faq_question / faq_answer / faq_classification /
related_cards) into workspace/rules_work.db.

Atomic unit = single item per INSERT; one COMMIT per source after all its
items are validated (items already INSERTed survive a later-source failure).
Re-runnable: all stage2d rows (notes LIKE '%stage2d faq%') are deleted first.

Does NOT modify canonical rules. rule_change_candidate is a tagging label
only. Cards DB is used solely for card-name -> card_key alignment.
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB = r"workspace/rules_work.db"
CARDS_DB = r"cards_bilingual.db"
EXTRACTED = r"extracted"
REPORTS = Path(r"workspace/reports")

SOURCES = [
    ("source_001", r"loltcg_pdfs__01_2025-12-03_裁判FAQ_251023.txt", "zh", "p001"),
    ("source_005", r"loltcg_pdfs__05_2026-04-15_铸魂淬炼系列_官方FAQ_260114.txt", "zh", "p005"),
    ("source_006", r"loltcg_pdfs__06_2026-04-15_铸魂淬炼系列_裁判FAQ.txt", "zh", "p0068"),
    ("source_007", r"loltcg_pdfs__07_2026-04-30_破限系列_官方FAQ.txt", "zh", "p007"),
    ("source_008", r"loltcg_pdfs__08_2026-05-13_破限系列_裁判FAQ_260511.txt", "zh", "p0068"),
    ("source_011", r"loltcg_pdfs__11_2026-08-13_612b1cd53f9f41baaf3c8734c1881a3b.txt", "zh", "p011"),
    ("source_012", r"riftbound_en_rules__01_2025-10-24_Core_Rules_Patch_Notes.txt", "en", "pen"),
    ("source_014", r"riftbound_en_rules__03_2025-12-05_Spiritforged_Patch_Notes.txt", "en", "pen"),
    ("source_016", r"riftbound_en_rules__05_2026-03-30_Unleashed_Patch_Notes.txt", "en", "pen"),
    ("source_019", r"riftbound_en_rules__08_2026-07-17_Vendetta_Patch_Notes.txt", "en", "pen"),
]

ID_PREFIX = {"zh": "EV-CN-FAQ", "en": "EV-EN-OE"}

# ---------- shared regexes ----------
PAGE_RE = re.compile(r"^=====\s*PAGE\s+(\d+)\s*=====\s*$")
NOISE_EXACT = {
    "PRIVACY NOTICE", "TERMS OF SERVICE", "COOKIE PREFERENCES",
    "RELATED ARTICLES", "RULES AND RELEASES", "ANNOUNCEMENTS",
}
DATE_LINE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}$")
TRADEMARK_RE = re.compile(r"^©\s|^are trademarks", re.I)
BYLINE_RE = re.compile(r"^(Rules and Releases|Announcements|Design[^|]*)\s*\|\s*\d{1,2}/\d{1,2}/\d{4}\s*$", re.I)

# zh markers
Q_MARK_RE = re.compile(r"^问[：:]\s*(.+)$")                       # 005
QW_NUM_RE = re.compile(r"^问题\s*(\d+(?:\.\d+)?)\s*[：:]\s*(.*)$")  # 001/006
QA_Q_RE = re.compile(r"^Q(\d*)\s*[：:]\s*(.*)$")
QA_A_RE = re.compile(r"^A(\d*)\s*[：:]\s*(.*)$")
ZH_SECTION_NUM_RE = re.compile(r"^\d\s*[.．、]\s*(.{1,30})$")     # 1.打出卡牌 / 4.其他
REV_HDR_RE = re.compile(r"^(.+?)（(?:修订后|新文本)）\s*$|^(.+?)\s*\[(?:新文本|修订后)\]\s*$")
RULE_NO_LINE_RE = re.compile(r"^(?:\[(?:CN|EN)\]\s*)?(\d{3}(?:(?:\.\d+[a-z]?)|(?:\.[a-z]))*\.?)\s*$")
ANS_MARK_RE = re.compile(r"^答[：:]\s*(.*)$")
REL_RULES_RE = re.compile(r"^相关规则[：:]\s*(.+)$")
BARE_Q_RE = re.compile(r"[?？]\s*$")
ZH_RULE_REF_RE = re.compile(r"(?<![\d.])(\d{3}(?:(?:\.\d+[a-z]?)|(?:\.[a-z]))+)\.?(?![\d(])")
BRACKET_CARD_RE = re.compile(r"【([^【】]+)】")
DASH_SEP_RE = re.compile(r"^[—–\-\s]{2,}$")

# en markers
EN_TAG_RE = re.compile(r"^(NEW SYSTEM|NEW RULE|CLARIFIED RULE|CLARIFIED|REMOVAL|EDIT)\s*[.:]\s*(.*)$", re.I)
EN_COOKIE_RE = re.compile(r"^(This website utilizes|advertising\. To learn more|Manage Preferences\b)", re.I)
EN_RULE_REF_RE = re.compile(r"(?<![\d./])(\d{3}\.\d+[a-z]?(?:\.\d+[a-z]?)*)\b")
EN_DATE_MASK_RE = re.compile(r"\d{1,2}/\d{1,2}/\d{4}")

SHORT_ANSWER_RE = re.compile(r"^(是的?|不|否|可以|能|不能|不可以|无法|不会|会|仍然|照常|正确)[。！!]?$")

CLS = ["example_only", "rule_interpretation", "additional_condition",
       "exception", "rule_change_candidate", "uncertain"]


# ---------- tokenizer ----------
def tokenize(lines, lang):
    """-> list of (kind,text,page); kind in {LINE, BLANK}. Noise skipped; page tracked."""
    toks = []
    page = 0
    in_related = False
    for raw in lines:
        line = raw.rstrip().strip()
        m = PAGE_RE.match(line)
        if m:
            page = int(m.group(1))
            continue
        if not line:
            toks.append(("BLANK", "", page))
            continue
        if lang == "en":
            if line in NOISE_EXACT:
                if line == "RELATED ARTICLES":
                    in_related = True
                continue
            if in_related:
                continue
            if TRADEMARK_RE.match(line) or DATE_LINE_RE.match(line) or EN_COOKIE_RE.match(line):
                continue
        toks.append(("LINE", line, page))
    return toks


def is_title_line(text):
    """Heuristic zh section/topic header: short, no sentence-final punct, not a marker."""
    if len(text) > 32 or len(text) < 2:
        return False
    if text.startswith(("●", "○", "◦", "·", "【", "[", "（", "(", "“", "「", "『")):
        return False
    if re.search(r"[【】\[\]（）()]", text):
        return False
    if text.endswith("部分"):
        return False
    if re.search(r"[。？！；：:”]$", text):
        return False
    if (Q_MARK_RE.match(text) or QW_NUM_RE.match(text) or QA_Q_RE.match(text)
            or QA_A_RE.match(text) or RULE_NO_LINE_RE.match(text) or REL_RULES_RE.match(text)
            or DASH_SEP_RE.match(text)):
        return False
    if text.startswith(("问题", "注：", "备注")):
        return False
    return True


class Item:
    __slots__ = ("q", "a", "topic", "page", "cls", "conf", "notes", "refs")

    def __init__(self, q, topic, page):
        self.q = q or ""
        self.a = []
        self.topic = topic
        self.page = page
        self.cls = None
        self.conf = 0.70
        self.notes = []
        self.refs = []

    def answer_text(self):
        return "\n".join(x for x in self.a if x is not None).strip()


def base_zh_classify(it):
    """Heuristic 6-class classification for zh FAQ items."""
    a = it.answer_text()
    q = it.q
    refs = ZH_RULE_REF_RE.findall(q + "\n" + a)
    it.refs = sorted(set(r.rstrip(".") for r in refs))
    has_card = bool(BRACKET_CARD_RE.search(q + a))
    # already pre-assigned by parser (e.g. revised-rule blocks)
    if it.cls:
        return it
    if ("（旧）" in a or "（原）" in a) and ("（新）" in a or "（修订后）" in a):
        it.cls, it.conf = "rule_change_candidate", 0.80
        return it
    if any(w in a for w in ("例外", "特例", "特殊规则", "特殊情况", "是一个规则上的特殊")):
        it.cls, it.conf = "exception", 0.75
        return it
    if has_card and not it.refs:
        it.cls, it.conf = "example_only", 0.70
    else:
        it.cls, it.conf = "rule_interpretation", 0.75 if it.refs else 0.70
    return it


# ---------- parser: source_001 (问题 N.M + interleaved Q/A) ----------
def parse_p001(toks):
    items, front = [], []
    topic = None
    it = None
    in_ans = False
    for kind, text, page in toks:
        if kind == "BLANK":
            continue
        msec = ZH_SECTION_NUM_RE.match(text)
        mqw = QW_NUM_RE.match(text)
        if it is None and front is not None and not mqw and not Q_MARK_RE.match(text) \
                and not QA_Q_RE.match(text) and not msec and len(items) == 0:
            front.append(text)
            continue
        if msec and not mqw:
            if it:
                items.append(it); it = None
            topic = msec.group(1).strip()
            continue
        if mqw:
            if it:
                items.append(it)
            it = Item(f"问题 {mqw.group(1)}：{mqw.group(2)}", topic, page)
            in_ans = False
            continue
        mq = QA_Q_RE.match(text)
        if mq:
            if it:
                items.append(it)
            it = Item(mq.group(2), topic, page)
            it.notes.append("qa_marker")
            in_ans = False
            continue
        ma = QA_A_RE.match(text)
        if ma and it:
            it.a.append(ma.group(2))
            in_ans = True
            continue
        if it:
            if not in_ans and not BARE_Q_RE.search(it.q):
                it.q = it.q + "\n" + text
            else:
                in_ans = True
                it.a.append(text)
        # stray lines with no open item: ignore (covered by front)
    if it:
        items.append(it)
    for it in items:
        base_zh_classify(it)
    return front, items


# ---------- parser: source_005 (问： + 修订后 blocks + topic headers) ----------
def parse_p005(toks):
    items, front = [], []
    topic = None
    it = None
    for kind, text, page in toks:
        if kind == "BLANK":
            continue
        mq = Q_MARK_RE.match(text)
        mrev = REV_HDR_RE.match(text)
        if mq:
            if it:
                items.append(it)
            it = Item("问：" + mq.group(1), topic, page)
            it.notes.append("qa_marker")
            continue
        if mrev:
            if it:
                items.append(it)
            name = (mrev.group(1) or mrev.group(2)).strip()
            it = Item(text, topic, page)
            it.notes.append("revised_block")
            if re.match(r"^规则", name):
                it.cls, it.conf = "rule_change_candidate", 0.85
                it.notes.append("faq_claims_core_rule_revision")
            else:
                it.cls, it.conf = "rule_interpretation", 0.75
                it.notes.append("mentions_errata; errata_extracted_in_stage2c")
            continue
        if it is None:
            if is_title_line(text) and text in ("现存问题", "功能性勘误", "规则阐明", "规则补充说明"):
                topic = text
            else:
                front.append(text)
            continue
        mans = ANS_MARK_RE.match(text)
        if mans:
            it.a.append(mans.group(1))
            continue
        if is_title_line(text) and len(text) <= 22 and not it.a:
            # header between items (rare) -> retopic
            topic = text
            it.topic = topic
            continue
        if is_title_line(text) and len(text) <= 22 and it.answer_text():
            items.append(it)
            it = None
            topic = text
            continue
        if "revised_block" in it.notes:
            it.a.append(text)
        elif not it.answer_text() and not BARE_Q_RE.search(it.q):
            it.q += "\n" + text
        else:
            it.a.append(text)
    if it:
        items.append(it)
    # retopic: front_only sources already handled
    for it in items:
        if it.topic is None:
            it.topic = topic
        base_zh_classify(it)
    return front, items


# ---------- parser: source_006 / source_008 (Q/A + Qn/An + bare Q&A) ----------
def parse_p0068(toks):
    lts = [(t, p) for k, t, p in toks if k == "LINE"]
    items, front = [], []
    topic = None
    it = None
    in_ans = False
    cur_qnum = 0
    pending_ctx = []

    def ctx_prefix():
        nonlocal pending_ctx
        p = ("\n".join(pending_ctx) + "\n") if pending_ctx else ""
        pending_ctx = []
        return p

    frac = []       # buffered open-ended lines (fractured question detection)
    frac_it = None  # item they were diverted from (None = pending_ctx zone)

    for i, (text, page) in enumerate(lts):
        nxt = lts[i + 1][0] if i + 1 < len(lts) else ""
        msec = ZH_SECTION_NUM_RE.match(text)
        mqw = QW_NUM_RE.match(text)
        mq = QA_Q_RE.match(text)
        ma = QA_A_RE.match(text)
        mrev = REV_HDR_RE.match(text)
        if frac:
            if BARE_Q_RE.search(text):
                if frac_it is not None and not BARE_Q_RE.search(frac_it.q):
                    # the question itself fractured across lines/pages: rejoin into q
                    frac_it.q = frac_it.q + "\n" + "\n".join(frac) + "\n" + text
                    it = frac_it
                    frac, frac_it = [], None
                    continue
                if frac_it is not None:
                    items.append(frac_it)
                it = Item(ctx_prefix() + "\n".join(frac) + "\n" + text, topic, page)
                it.notes.append("unmarked_qa")
                it.conf = 0.55
                in_ans = False
                cur_qnum = 0
                frac, frac_it = [], None
                continue
            if msec or mqw or mq or ma or mrev:
                if frac_it is not None:
                    frac_it.a.extend(frac)
                    items.append(frac_it)
                    frac_it = None
                else:
                    pending_ctx = frac + pending_ctx
                frac = []
                # fall through to marker handling
            elif text.endswith(("。", "！", "”", "：", ":")):
                if frac_it is not None:
                    frac_it.a.extend(frac + [text])
                    it = frac_it
                else:
                    pending_ctx = frac + [text] + pending_ctx
                frac, frac_it = [], None
                continue
            else:
                frac.append(text)
                continue
        started = len(items) > 0 or it is not None
        if not started and not msec and not mqw and not mq:
            front.append(text)
            continue
        if msec:
            if it:
                items.append(it); it = None
            topic = msec.group(1).strip()
            pending_ctx = []
            continue
        if mrev:
            if it:
                items.append(it)
            it = Item(ctx_prefix() + text, topic, page)
            it.notes.append("revised_block")
            it.notes.append("mentions_errata; errata_extracted_in_stage2c")
            it.cls, it.conf = "rule_interpretation", 0.75
            in_ans = True
            cur_qnum = 0
            continue
        if mqw:
            if it:
                items.append(it)
            q = f"问题 {mqw.group(1)}：{mqw.group(2)}"
            it = Item(ctx_prefix() + q, topic, page)
            # if the 问题 header line has no "?", following lines are narrative answer
            in_ans = not BARE_Q_RE.search(q)
            cur_qnum = 0
            continue
        if mq:
            num = int(mq.group(1)) if mq.group(1) else 0
            body = mq.group(2).strip()
            # typo guard: "Q：可以。" style answer mislabel (source_006 l.37)
            if it is not None and num == 0 and SHORT_ANSWER_RE.match(body) \
                    and BARE_Q_RE.search(it.q):
                it.a.append(body)
                it.notes.append("typo_fixed: Q marker interpreted as A")
                in_ans = True
                continue
            if num > 1 and it is not None and cur_qnum == num - 1:
                it.q += "\n" + text
                cur_qnum = num
                in_ans = False
                continue
            # enumerated Q1..Qn options following a scenario bare-question belong to it
            if num == 1 and it is not None and "unmarked_qa" in it.notes \
                    and not it.answer_text():
                it.q += "\n" + text
                cur_qnum = 1
                in_ans = False
                continue
            if it:
                items.append(it)
            it = Item(ctx_prefix() + text, topic, page)
            it.notes.append("qa_marker")
            in_ans = False
            cur_qnum = num
            continue
        if ma:
            if it:
                num = int(ma.group(1)) if ma.group(1) else 0
                if num > 1:
                    it.a.append("A%d：%s" % (num, ma.group(2)))
                else:
                    it.a.append(ma.group(2))
                in_ans = True
            continue
        # fractured question candidate: open-ended line -> buffer until resolved
        if not BARE_Q_RE.search(text) and not text.endswith(("。", "！", "”", "：", ":")) \
                and (it is None or in_ans) and not is_title_line(text):
            frac = pending_ctx + [text]
            pending_ctx = []
            frac_it = it
            it = None
            continue
        # multi-sentence question continuation: q already has "?" but this line
        # keeps asking and the next line ends with "?" (e.g. "...抽牌？/在满足...宝/石】？")
        if it is not None and not in_ans and not it.answer_text() \
                and it.q.rstrip().endswith(("？", "?")) \
                and not BARE_Q_RE.search(text) and BARE_Q_RE.search(nxt):
            it.q += "\n" + text
            continue
        # question tail line (e.g. "石】？") while previous q-line is unclosed
        if it is not None and not in_ans and not it.answer_text() \
                and not it.q.rstrip().endswith(("？", "?")) and BARE_Q_RE.search(text):
            it.q += "\n" + text
            continue
        # bare question line opens a new item (unmarked structure)
        if BARE_Q_RE.search(text) and (it is None or in_ans):
            if it:
                items.append(it)
            it = Item(ctx_prefix() + text, topic, page)
            it.notes.append("unmarked_qa")
            it.conf = 0.55
            in_ans = False
            cur_qnum = 0
            continue
        # title-ish line between items -> context/topic hint
        if it is None and is_title_line(text):
            pending_ctx.append(text)
            continue
        if it:
            if "revised_block" in it.notes:
                it.a.append(text)
            elif not in_ans and not it.answer_text() and not BARE_Q_RE.search(it.q):
                it.q += "\n" + text
            else:
                it.a.append(text)
                in_ans = True
        else:
            nxt_is_q = bool(QA_Q_RE.match(nxt) or QW_NUM_RE.match(nxt) or BARE_Q_RE.search(nxt))
            if (len(text) > 40 or text.endswith("。")) and not nxt_is_q:
                # long prose passage without question marker (e.g. src008 sec.4 analysis)
                q0 = ctx_prefix() or topic
                it = Item(q0, topic, page)
                it.notes.append("prose_passage")
                it.a.append(text)
                in_ans = True
            else:
                pending_ctx.append(text)
    if frac:
        if frac_it is not None:
            frac_it.a.extend(frac)
            it = frac_it
        else:
            front.extend(frac)
    if it:
        items.append(it)
    for it in items:
        base_zh_classify(it)
        if "unmarked_qa" in it.notes:
            it.conf = 0.55
    return front, items


# ---------- parser: source_007 (prose rule-revision + Q&A + rule-quote blocks) ----------
def parse_p007(toks):
    items, front = [], []
    topic = None
    it = None
    in_quote = False
    in_quote2 = False
    started = False
    for kind, text, page in toks:
        if kind == "BLANK":
            in_quote = False
            continue
        mrule = RULE_NO_LINE_RE.match(text)
        # curly-quote citation block: “... possibly spanning lines until closing ”
        if started and it is not None:
            if in_quote2:
                it.a.append(text)
                if text.endswith("”") or text.endswith('” ') or "”" in text:
                    in_quote2 = False
                continue
            if text.startswith("“") and not text.endswith("”"):
                it.a.append(text)
                in_quote2 = True
                continue
        if not started and not mrule and not BARE_Q_RE.search(text):
            if is_title_line(text) and front:
                # first content section header after doc preamble -> start prose item
                it = Item(text, text, page)
                it.notes.append("prose_section")
                topic = text
                started = True
            else:
                front.append(text)
            continue
        if is_title_line(text) and len(text) <= 14 and not in_quote:
            if it is not None and not it.answer_text() and "prose_section" in it.notes:
                # parent header with no body yet: merge as topic hierarchy
                it.q = it.q + " / " + text
                it.topic = it.q
                topic = it.q
            else:
                if it:
                    items.append(it)
                it = Item(text, text, page)
                it.notes.append("prose_section")
                topic = text
            started = True
            continue
        if mrule:
            ref = mrule.group(1).rstrip(".")
            if it is None:
                it = Item(text, topic, page)
                it.notes.append("rule_quote_block")
                started = True
            else:
                it.a.append(text)
            it.refs.append(ref)
            in_quote = True
            continue
        if BARE_Q_RE.search(text) and not in_quote:
            if it:
                items.append(it)
            it = Item(text, topic, page)
            started = True
            continue
        if it is None:
            it = Item(text, topic, page)
            it.notes.append("prose_section")
            started = True
            continue
        it.a.append(text)
    if it:
        items.append(it)
    for it in items:
        base_zh_classify(it)
        if it.cls is None:
            it.cls = "rule_interpretation"
        if "prose_section" in it.notes and it.cls == "rule_interpretation":
            it.conf = 0.70
    return front, items


# ---------- parser: source_011 (question-heading + 相关规则 refs) ----------
def parse_p011(toks):
    lts = [(t, p) for k, t, p in toks if k == "LINE"]
    items, front = [], []
    topic = None
    it = None
    started = False
    pending = []
    for i, (text, page) in enumerate(lts):
        nxt = lts[i + 1][0] if i + 1 < len(lts) else ""
        if DASH_SEP_RE.match(text):
            continue
        mrel = REL_RULES_RE.match(text)
        if not started and not BARE_Q_RE.search(text) and not mrel:
            front.append(text)
            continue
        if BARE_Q_RE.search(text):
            if it:
                items.append(it)
            q = (("\n".join(pending) + "\n") if pending else "") + text
            pending = []
            it = Item(q, topic, page)
            started = True
            continue
        # fractured question: open-ended line in answer zone followed by "?"-line
        if it is not None and it.answer_text() and not BARE_Q_RE.search(text) \
                and not text.endswith(("。", "！", "”", "：", ":")) and BARE_Q_RE.search(nxt):
            items.append(it)
            it = None
            pending.append(text)
            continue
        if it is None:
            # short topic line acting as header (e.g. card name) -> attach to next q
            topic = text if len(text) <= 32 else topic
            if len(text) <= 32 and not text.endswith(("。", "！", "：")):
                continue
            it = Item(text, topic, page)
            started = True
            continue
        if mrel:
            it.refs.extend(r.rstrip(".") for r in ZH_RULE_REF_RE.findall(mrel.group(1)))
            it.a.append(text)
            continue
        it.a.append(text)
    if it:
        items.append(it)
    for it in items:
        if it.topic and it.topic not in it.q and len(it.topic) <= 32:
            it.q = it.topic + "\n" + it.q
        base_zh_classify(it)
        if it.cls is None:
            it.cls = "rule_interpretation"
    return front, items


# ---------- parser: EN patch notes (NEW/CLARIFIED markers) ----------
EN_CLASS_MAP = {
    "NEW SYSTEM": ("rule_change_candidate", "high"),
    "NEW RULE": ("rule_change_candidate", "high"),
    "EDIT": ("rule_change_candidate", "high"),
    "REMOVAL": ("rule_change_candidate", "high"),
    "CLARIFIED RULE": ("rule_interpretation", "high"),
    "CLARIFIED": ("rule_interpretation", "high"),
}


def is_en_section(text):
    if len(text) > 70 or len(text) < 3:
        return False
    if text.endswith((".", "!", "?")):
        return False
    if EN_TAG_RE.match(text):
        return False
    # section headers start with uppercase/digit/symbol; lowercase-start lines are prose
    if not (text[0].isupper() or text[0].isdigit() or text[0] in "[(“\"'"):
        return False
    return True


def parse_pen(toks):
    items, front = [], []
    topic = None
    it = None
    cur = []   # paragraph buffer
    cur_page = 0
    seen_marker = False

    def flush_para():
        nonlocal cur
        if not cur:
            return None, None
        para = " ".join(cur)
        cur = []
        return para, cur_page

    def emit_para(para, ppage):
        nonlocal it
        if para is None:
            return
        if it is not None:
            it.a.append(para)
        elif seen_marker:
            pit = Item(None, topic, ppage or 1)
            pit.notes.append("prose_passage")
            pit.cls, pit.conf = "rule_interpretation", 0.75
            pit.a.append(para)
            items.append(pit)
        else:
            front.append(para)

    for kind, text, page in toks:
        if kind == "BLANK":
            para, ppage = flush_para()
            emit_para(para, ppage)
            continue
        if BYLINE_RE.match(text):
            para, ppage = flush_para()
            emit_para(para, ppage)
            if it is None:
                front.append(text)
            continue
        mtag = EN_TAG_RE.match(text)
        if mtag:
            para, ppage = flush_para()
            emit_para(para, ppage)
            if it:
                items.append(it)
            seen_marker = True
            it = Item(text, topic, page if page else cur_page)
            marker = mtag.group(1).upper()
            cls, conf = EN_CLASS_MAP[marker]
            it.cls = cls
            it.conf = 0.85
            it.notes.append(f"marker={marker}")
            continue
        if (it is not None or items) and is_en_section(text) and not cur:
            if it:
                items.append(it)
                it = None
            topic = text
            continue
        if not cur:
            cur_page = page
        cur.append(text)
    para, ppage = flush_para()
    emit_para(para, ppage)
    if it:
        items.append(it)
    for it in items:
        refs = EN_RULE_REF_RE.findall(EN_DATE_MASK_RE.sub("", it.q + "\n" + it.answer_text()))
        it.refs = sorted(set(refs))
    return front, items


PARSERS = {"p001": parse_p001, "p005": parse_p005, "p0068": parse_p0068,
           "p007": parse_p007, "p011": parse_p011, "pen": parse_pen}


# ---------- card alignment ----------
def load_card_index():
    ccon = sqlite3.connect(CARDS_DB)
    rows = ccon.execute("SELECT card_key, name_cn, sub_title_cn, name_en FROM cards").fetchall()
    ccon.close()
    zh_main, zh_full, en_map = {}, {}, {}
    for key, ncn, sub, nen in rows:
        if ncn:
            zh_main.setdefault(ncn.strip(), []).append(key)
            if sub:
                zh_full.setdefault(f"{ncn.strip()} - {sub.strip()}", []).append(key)
        if nen:
            en_map.setdefault(nen.strip().lower(), []).append(key)
    return zh_main, zh_full, en_map


def align_cards_zh(text, zh_main, zh_full):
    # card names may wrap across lines inside 【】; strip inner newlines when matching
    names, ids = [], []
    for m in BRACKET_CARD_RE.findall(text):
        nm = re.sub(r"\s*\n\s*", "", m).strip().replace("「", "").replace("」", "")
        if not nm:
            continue
        names.append(nm)
        keys = zh_full.get(nm) or zh_main.get(nm.split(" - ")[0].strip())
        if keys:
            ids.extend(keys)
    return sorted(set(names)), sorted(set(ids))


def align_cards_en(text, en_map):
    low = text.lower()
    names, ids = [], []
    for nm, keys in en_map.items():
        if re.search(r"(?<![a-z])" + re.escape(nm) + r"(?![a-z])", low):
            names.append(nm)
            ids.extend(keys)
    return sorted(set(names)), sorted(set(ids))


def conf_bucket(c):
    return "high" if c >= 0.80 else ("medium" if c >= 0.60 else "low")


# ---------- main ----------
def main():
    only = None
    if "--source" in sys.argv:
        only = sys.argv[sys.argv.index("--source") + 1]

    zh_main, zh_full, en_map = load_card_index()
    con = sqlite3.connect(DB)
    cols = [r[1] for r in con.execute("PRAGMA table_info(evidence)")]
    if "card_ids" not in cols:
        con.execute("ALTER TABLE evidence ADD COLUMN card_ids TEXT")
    srows = {r[0]: r for r in con.execute(
        "SELECT source_id, source_type, source_document, version, date FROM sources")}

    counters = {}
    for lang, pref in ID_PREFIX.items():
        row = con.execute(
            "SELECT MAX(evidence_id) FROM evidence WHERE evidence_id LIKE ?",
            (pref + "-%",)).fetchone()
        counters[lang] = int(row[0].rsplit("-", 1)[1]) if row and row[0] else 0

    def next_id(lang):
        counters[lang] += 1
        return f"{ID_PREFIX[lang]}-{counters[lang]:04d}"

    stats = {"sources": {}, "totals": {"items": 0, "front_matter": 0, "needs_review": 0},
             "classification": {c: 0 for c in CLS}}

    for sid, fname, lang, parser_key in SOURCES:
        if only and sid != only:
            continue
        path = Path(EXTRACTED) / fname
        if not path.exists():
            print(f"[FAIL] {sid}: missing {path}")
            con.execute(
                "UPDATE processing_tasks SET status='failed', notes=COALESCE(notes,'') || ?"
                " WHERE task_id LIKE ?", ("; Stage2D FAILED: extracted txt missing", sid + "%"))
            con.commit()
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        toks = tokenize(lines, lang)
        front, items = PARSERS[parser_key](toks)

        # re-run safety: wipe this source's previous stage2d rows
        con.execute(
            "DELETE FROM evidence WHERE source_id=? AND notes LIKE '%stage2d faq%'", (sid,))

        _, stype, sdoc, sver, sdate = srows[sid]
        count, nrev = 0, 0

        # front matter evidence
        front_txt = "\n".join(t.strip() for t in front if t and t.strip()).strip()
        if front_txt:
            ev = next_id(lang)
            con.execute(
                "INSERT INTO evidence (evidence_id, topic, source_id, source_type, source_language,"
                " source_document, version, date, page, section, original_text,"
                " normalized_summary, confidence, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ev, "front_matter", sid, stype, lang, sdoc, sver, sdate, 1, "main",
                 front_txt, "FAQ/OE document header, scope and authority statements",
                 "high", "structural_extraction; stage2d faq; front_matter"))
            stats["totals"]["front_matter"] += 1

        for it in items:
            q = it.q.strip()
            a = it.answer_text()
            if not q and not a:
                continue
            original = (q + "\n\n" + a).strip() if a else q
            if lang == "zh":
                rc, cids = align_cards_zh(original, zh_main, zh_full)
            else:
                rc, cids = align_cards_en(original, en_map)
            needs_review = ("unmarked_qa" in it.notes) or ("typo_fixed" in it.notes)
            if it.cls == "uncertain":
                needs_review = True
            notes = {"parse": it.notes, "needs_review": needs_review}
            if it.refs:
                notes["related_rule_refs"] = sorted(set(it.refs))
            ev = next_id(lang)
            con.execute(
                "INSERT INTO evidence (evidence_id, rule_id_candidate, topic, source_id, source_type,"
                " source_language, source_document, version, date, page, section, original_text,"
                " normalized_summary, confidence, notes,"
                " faq_question, faq_answer, faq_classification, related_cards, card_ids)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (ev, (it.refs[0] if it.refs else None), it.topic, sid, stype, lang,
                 sdoc, sver, sdate, it.page, "main", original,
                 ("FAQ: " + q[:110]) if q else ("OE entry: " + a[:110]),
                 conf_bucket(it.conf),
                 "structural_extraction; stage2d faq; " + json.dumps(notes, ensure_ascii=False),
                 q or None, a or None, it.cls,
                 json.dumps(rc, ensure_ascii=False) if rc else None,
                 json.dumps(cids, ensure_ascii=False) if cids else None))
            count += 1
            nrev += 1 if needs_review else 0
            stats["classification"][it.cls] = stats["classification"].get(it.cls, 0) + 1

        con.execute(
            "UPDATE processing_tasks SET status='completed', notes=COALESCE(notes,'') || ?"
            " WHERE task_id LIKE ?",
            (f"; Stage2D: extracted {count} items (needs_review={nrev})", sid + "%"))
        con.commit()
        stats["sources"][sid] = {"items": count, "needs_review": nrev,
                                 "pages": path.read_text(encoding='utf-8').count("===== PAGE")}
        stats["totals"]["items"] += count
        stats["totals"]["needs_review"] += nrev
        print(f"[OK] {sid} ({parser_key}): {count} items, needs_review={nrev}")

    con.commit()
    con.close()
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "stage2d_stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats["totals"], ensure_ascii=False))
    print(json.dumps(stats["classification"], ensure_ascii=False))


if __name__ == "__main__":
    main()
