# -*- coding: utf-8 -*-
"""卡名识别（提及解析）：别名索引 + 确定性优先的提及解析

别名索引来源：
    - cards_bilingual.db 的 cards 表（全量；缺失/读取失败时降级并打印 stderr 警告）
    - rules.db 中 R-CARD 类规则的 topic（形如 "card:OGN-242 (Baited Hook / 海兽钓钩)"
      或 "card:ARC-001 (蔚)"），作为别名与名字的补充来源

解析顺序（确定性，默认路径）：
    1. card-id 正则命中（如 OGN-242，大小写不敏感）→ exact
    2. 引号片段（《》「」"" 内文本）优先按别名词典查
    3. 别名词典在 query 上的最长匹配扫描（重叠取更长者，已命中区间不重复解析）
未命中提及再做字符重叠模糊匹配（唯一 card_key 才解析，多个则 ambiguous）；
unresolved 提及按有界重试（更宽上下文窗口）后再判定。

可选 LLM 辅助（默认关闭，llm callable 通过构造参数注入，本模块不 import openai）：
    RAG_LLM_CARD_EXTRACTION=1  确定性抽取一无所获后，调用 llm_extract(query) 提出
                               额外名字字符串（仍必须过本地索引解析）
    RAG_LLM_CARD_SELECTION=1   ambiguous 候选交 llm_select(mention, card_ids) 选一个，
                               返回未知 id 一律拒绝

环境变量：
    RAG_CARDS_DB_PATH            cards DB 路径（默认仓库根 cards_bilingual.db）
    RAG_CARD_RESOLUTION_TOP_K    模糊候选条数（默认 5）
    RAG_CARD_RESOLUTION_RETRY    unresolved 重试次数（默认 1）
    RAG_LLM_CARD_EXTRACTION      见上（默认关）
    RAG_LLM_CARD_SELECTION       见上（默认关）

纯 stdlib（sqlite3/re/os/json）。
"""
import json
import os
import re
import sqlite3
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CARDS_DB = os.path.join(ROOT, "cards_bilingual.db")

# card-id：SET(2-4 字母)-3 位数字 + 可选变体后缀（大小写不敏感，命中后规范化大写）
_RE_CARD_ID = re.compile(r"[A-Za-z]{2,4}-\d{3}[a-zA-Z]?")
# R-CARD topic："card:<id> (<EN> / <CN>)" 或只有 CN
_RE_TOPIC = re.compile(r"^card:([^\s()]+)\s*(?:\((.*)\))?\s*$")
# 引号片段
_RE_QUOTED = re.compile(r"[《「\"“]([^《》「」\"“”]{1,40}?)[》」\"”]")

# 归一化时映射为空格的字符
_SPACE_CHARS = u"·・"
# 归一化时去掉的标点（全长/半角常见标点，含引号书名号）
_PUNCT_DROP = set(u"《》「」\"“”'‘’、，。．,.:：;；!！?？()（）[]［］【】{}<>/\\|*-—_~^")

# 别名种类权重：组合全名 > id > 裸名（同名变体裁决用）
_KIND_WEIGHT = {"full": 3, "id": 2, "name": 1}
# 重试时的上下文窗口宽度（字符）
_RETRY_WINDOW = 8


def _env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default


def _env_flag(name):
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def normalize(text):
    """归一化：·/・→空格、去书名号/引号与常见标点、拉丁 casefold、压缩空白。"""
    out, _, _ = _normalize_with_map(text)
    return out


def _normalize_with_map(text):
    """normalize + 每个归一化字符在原文中的下标（命中区间映射回原文用）。"""
    out, amap = [], []
    prev_space = True
    for i, ch in enumerate(text or ""):
        if ch in _SPACE_CHARS or ch.isspace():
            c = " "
        elif ch in _PUNCT_DROP:
            continue
        else:
            c = ch.casefold()
        if c == " ":
            if prev_space:
                continue
            out.append(c)
            amap.append(i)
            prev_space = True
        else:
            out.append(c)
            amap.append(i)
            prev_space = False
    while out and out[-1] == " ":
        out.pop()
        amap.pop()
    return "".join(out), amap, prev_space


def _alias_len_ok(s):
    """别名长度下限：>=2，或含 CJK 的单字（如卡名 "蔚"）。"""
    return len(s) >= 2 or (len(s) >= 1
                           and any(u"一" <= ch <= u"鿿" for ch in s))


def _overlap_score(a, b):
    """最长公共子串长度（O(n*m) DP；别名都很短）。"""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


class CardResolver:
    """卡名提及解析器：构建别名索引并提供 resolve(query)。"""

    def __init__(self, rules_db_path=None, cards_db_path=None,
                 llm_extract=None, llm_select=None, retry=None, top_k=None):
        if rules_db_path is None:
            import rag_query  # 延迟 import：便于测试用 fixture DB，不依赖真实路径
            rules_db_path = rag_query.DB
        if cards_db_path is None:
            cards_db_path = os.environ.get("RAG_CARDS_DB_PATH") or DEFAULT_CARDS_DB
        self.rules_db_path = rules_db_path
        self.cards_db_path = cards_db_path
        self.llm_extract = llm_extract
        self.llm_select = llm_select
        self.retry = _env_int("RAG_CARD_RESOLUTION_RETRY", 1) if retry is None else retry
        self.top_k = (_env_int("RAG_CARD_RESOLUTION_TOP_K", 5)
                      if top_k is None else top_k)
        # card_key -> {"name_cn","name_en","sub_title_cn"}
        self.cards = {}
        # id（大写形式）-> card_key
        self.id_index = {}
        # 原始别名 -> {card_key: kind}
        self.alias_index = {}
        # 归一化别名 -> {card_key: kind}（仅收录 norm != 原始形式 的别名）
        self.norm_index = {}
        self._load()

    # ---------- 索引构建 ----------

    def _load(self):
        self._load_cards_db()
        self._load_rule_topics()

    def _load_cards_db(self):
        if not os.path.exists(self.cards_db_path):
            print("card_resolver: cards DB 不存在，降级为规则库卡名索引: %s"
                  % self.cards_db_path, file=sys.stderr)
            return
        try:
            db = sqlite3.connect(self.cards_db_path)
            try:
                rows = db.execute(
                    "SELECT card_key, name_en, name_cn, sub_title_cn FROM cards"
                ).fetchall()
            finally:
                db.close()
        except Exception as exc:
            print("card_resolver: cards DB 读取失败，降级为规则库卡名索引: %s"
                  % exc, file=sys.stderr)
            return
        for card_key, name_en, name_cn, sub_title_cn in rows:
            self._add_card(card_key, name_cn, name_en, sub_title_cn)

    def _load_rule_topics(self):
        try:
            db = sqlite3.connect(self.rules_db_path)
            try:
                rows = db.execute(
                    "SELECT topic FROM rules WHERE topic LIKE 'card:%'"
                ).fetchall()
            finally:
                db.close()
        except Exception as exc:
            print("card_resolver: rules DB 读取失败，R-CARD 别名不可用: %s"
                  % exc, file=sys.stderr)
            return
        for (topic,) in rows:
            m = _RE_TOPIC.match(topic or "")
            if not m:
                continue
            card_id = m.group(1)
            names = [p.strip() for p in (m.group(2) or "").split("/") if p.strip()]
            name_en, name_cn = None, None
            if len(names) >= 2:
                name_en, name_cn = names[0], names[-1]
            elif names:
                # 只有一段时按是否含拉丁字母粗判
                if re.search(r"[A-Za-z]", names[0]):
                    name_en = names[0]
                else:
                    name_cn = names[0]
            self._add_card(card_id, name_cn, name_en, None)

    def _add_card(self, card_key, name_cn, name_en, sub_title_cn):
        info = self.cards.get(card_key)
        if info is None:
            info = {"name_cn": None, "name_en": None, "sub_title_cn": None}
            self.cards[card_key] = info
        # 后到的非空值补齐，不覆盖已有值
        for k, v in (("name_cn", name_cn), ("name_en", name_en),
                     ("sub_title_cn", sub_title_cn)):
            if v and not info.get(k):
                info[k] = v
        self.id_index[card_key.upper()] = card_key
        self._add_alias(card_key, card_key, "id")
        cn = info.get("name_cn")
        en = info.get("name_en")
        sub = info.get("sub_title_cn")
        if cn:
            self._add_alias(card_key, cn, "name")
            # name_cn 本身含空格（如 "斥候标兵 艾娃"）时，末段作为裸名别名
            parts = cn.split()
            if len(parts) > 1:
                self._add_alias(card_key, parts[-1], "name")
        if en:
            self._add_alias(card_key, en, "name")
        if sub and cn:
            # 组合全名两种顺序均为更强形式（full）
            self._add_alias(card_key, u"%s %s" % (sub, cn), "full")
            self._add_alias(card_key, u"%s %s" % (cn, sub), "full")

    def _add_alias(self, card_key, alias, kind):
        alias = (alias or "").strip()
        if not _alias_len_ok(alias):
            return
        self.alias_index.setdefault(alias, {})[card_key] = kind
        na = normalize(alias)
        if _alias_len_ok(na) and na != alias:
            self.norm_index.setdefault(na, {})[card_key] = kind

    # ---------- 公开接口 ----------

    def resolve(self, query):
        """返回 {"resolved": [...], "ambiguous": [...], "unresolved": [...]}"""
        query = query or ""
        norm_q, amap, _ = _normalize_with_map(query)
        occupied = []  # 已命中的原文区间 [s, e)
        resolved, ambiguous, unresolved = [], [], []

        def overlaps(s, e):
            return any(s < oe and os_ < e for os_, oe in occupied)

        # 1) card-id 正则 → exact
        for m in _RE_CARD_ID.finditer(query):
            s, e = m.span()
            if overlaps(s, e):
                continue
            card_key = self.id_index.get(m.group().upper(), m.group().upper())
            resolved.append(self._resolved_item(card_key, query[s:e], "exact",
                                                "deterministic"))
            occupied.append((s, e))

        # 2) 引号片段优先按字典查；未命中进待决列表（fuzzy → 重试）
        pending = []  # {"mention","span","ctx"}
        for m in _RE_QUOTED.finditer(query):
            s, e = m.span(1)
            if overlaps(s, e):
                continue
            mention = query[s:e]
            hit = self._match_alias_text(mention)
            if hit is None:
                pending.append({
                    "mention": mention,
                    "span": (s, e),
                    "ctx": query[max(0, s - _RETRY_WINDOW): e + _RETRY_WINDOW],
                })
                continue
            confidence, key2kind = hit
            if len(key2kind) == 1:
                card_key = next(iter(key2kind))
                resolved.append(self._resolved_item(card_key, mention, confidence,
                                                    "deterministic"))
            else:
                ambiguous.append(self._ambiguous_item(mention, key2kind))
            occupied.append((s, e))

        # 3) 别名词典最长匹配扫描（归一化坐标系，重叠取更长者）
        for ns, ne, ainfo in self._scan_aliases(norm_q):
            rs, re_ = amap[ns], amap[ne - 1] + 1
            if overlaps(rs, re_):
                continue
            mention = query[rs:re_]
            key2kind = self._pick_stronger(ainfo["keys"])
            if len(key2kind) == 1:
                card_key = next(iter(key2kind))
                resolved.append(self._resolved_item(card_key, mention,
                                                    ainfo["confidence"],
                                                    "deterministic"))
            else:
                ambiguous.append(self._ambiguous_item(mention, key2kind))
            occupied.append((rs, re_))

        # 4) 待决提及：模糊匹配 → 有界重试（更宽上下文窗口）
        for item in pending:
            resolved_one = self._settle_pending(item, resolved, ambiguous)
            if not resolved_one:
                unresolved.append(item["mention"])

        # 5) 可选 LLM 辅助抽取（默认关闭）：确定性抽取一无所获后才调用
        if (_env_flag("RAG_LLM_CARD_EXTRACTION") and self.llm_extract
                and not (resolved or ambiguous or unresolved)):
            for name in self._call_llm_extract(query):
                pos = query.find(name)
                ctx = (query[max(0, pos - _RETRY_WINDOW): pos + len(name) + _RETRY_WINDOW]
                       if pos >= 0 else query)
                item = {"mention": name, "span": None, "ctx": ctx}
                if not self._settle_pending(item, resolved, ambiguous,
                                            source="llm_extract"):
                    unresolved.append(name)

        # 6) 可选 LLM 候选仲裁（默认关闭）：未知 id 一律拒绝
        if _env_flag("RAG_LLM_CARD_SELECTION") and self.llm_select and ambiguous:
            still = []
            for amb in ambiguous:
                cand_ids = [c["card_id"] for c in amb["candidates"]]
                chosen = self.llm_select(amb["mention"], cand_ids)
                if chosen in cand_ids:
                    resolved.append(self._resolved_item(chosen, amb["mention"],
                                                        "fuzzy", "llm_select"))
                else:
                    still.append(amb)
            ambiguous = still

        return {"resolved": resolved, "ambiguous": ambiguous,
                "unresolved": unresolved}

    def resolve_name(self, mention):
        """单个别名/提及查询（agent 工具用）：exact → normalized → fuzzy（不重试）。

        返回与 resolve() 同构的单项结构：
        {"resolved": [...], "ambiguous": [...], "unresolved": [...]}
        """
        mention = (mention or "").strip()
        empty = {"resolved": [], "ambiguous": [], "unresolved": [mention] if mention else []}
        if not mention:
            return empty
        # card-id 字面优先
        if _RE_CARD_ID.fullmatch(mention):
            card_key = self.id_index.get(mention.upper(), mention.upper())
            return {"resolved": [self._resolved_item(card_key, mention, "exact",
                                                     "deterministic")],
                    "ambiguous": [], "unresolved": []}
        hit = self._match_alias_text(mention)
        if hit is not None:
            confidence, key2kind = hit
            if len(key2kind) == 1:
                return {"resolved": [self._resolved_item(next(iter(key2kind)),
                                                         mention, confidence,
                                                         "deterministic")],
                        "ambiguous": [], "unresolved": []}
            return {"resolved": [],
                    "ambiguous": [self._ambiguous_item(mention, key2kind)],
                    "unresolved": []}
        outcome = self._resolve_fuzzy(mention)
        if outcome[0] == "resolved":
            return {"resolved": [self._resolved_item(outcome[1], mention, "fuzzy",
                                                     "deterministic")],
                    "ambiguous": [], "unresolved": []}
        if outcome[0] == "ambiguous":
            return {"resolved": [],
                    "ambiguous": [self._ambiguous_item(mention, outcome[1])],
                    "unresolved": []}
        return empty

    # ---------- 内部：提及落锤 ----------

    def _settle_pending(self, item, resolved, ambiguous, source="deterministic"):
        """对未命中提及依次尝试：字典 → fuzzy → 有界重试；成功返回 True。"""
        mention = item["mention"]
        hit = self._match_alias_text(mention)
        if hit is not None:
            confidence, key2kind = hit
            if len(key2kind) == 1:
                resolved.append(self._resolved_item(next(iter(key2kind)), mention,
                                                    confidence, source))
            else:
                ambiguous.append(self._ambiguous_item(mention, key2kind))
            return True
        outcome = self._resolve_fuzzy(mention)
        if outcome[0] == "resolved":
            resolved.append(self._resolved_item(outcome[1], mention, "fuzzy", source))
            return True
        if outcome[0] == "ambiguous":
            ambiguous.append(self._ambiguous_item(mention, outcome[1]))
            return True
        # 有界重试：在更宽上下文窗口上重扫别名 / 重算模糊匹配
        for _ in range(max(0, self.retry)):
            ctx = item.get("ctx") or mention
            nctx, _, _ = _normalize_with_map(ctx)
            for _, _, ainfo in self._scan_aliases(nctx):
                key2kind = self._pick_stronger(ainfo["keys"])
                if len(key2kind) == 1:
                    resolved.append(self._resolved_item(next(iter(key2kind)), mention,
                                                        "normalized", source))
                    return True
            outcome = self._resolve_fuzzy(ctx)
            if outcome[0] == "resolved":
                resolved.append(self._resolved_item(outcome[1], mention, "fuzzy",
                                                    source))
                return True
            if outcome[0] == "ambiguous":
                ambiguous.append(self._ambiguous_item(mention, outcome[1]))
                return True
        return False

    # ---------- 内部：匹配与选择 ----------

    def _match_alias_text(self, text):
        """整段文本按别名词典查；返回 (confidence, {card_key: kind}) 或 None。"""
        text = (text or "").strip()
        if not _alias_len_ok(text):
            return None
        if text in self.alias_index:
            return "exact", self._pick_stronger(dict(self.alias_index[text]))
        nt = normalize(text)
        if not _alias_len_ok(nt):
            return None
        # 归一化形式命中（含拉丁大小写不敏感）
        keys = self._lookup_norm(nt)
        if keys:
            return "normalized", self._pick_stronger(keys)
        return None

    def _lookup_norm(self, nt):
        """归一化别名查表（alias_index 中 norm==raw 的别名也在此命中）。"""
        keys = {}
        for alias, key2kind in self.alias_index.items():
            if normalize(alias) == nt:
                keys.update(key2kind)
        if nt in self.norm_index:
            keys.update(self.norm_index[nt])
        return keys

    def _scan_aliases(self, norm_q):
        """在归一化文本上扫描全部别名，返回不重叠命中（重叠取更长者）。

        每项 (ns, ne, {"confidence":..., "keys": {card_key: kind}})，按起点升序。
        """
        merged = {}  # 归一化别名 -> {"confidence","keys"}
        for alias, key2kind in self.alias_index.items():
            na = normalize(alias)
            if not _alias_len_ok(na):
                continue
            # 仅大小写差异视为 exact；标点/·/空白形态差异才算 normalized
            conf = "exact" if na == alias.casefold() else "normalized"
            entry = merged.setdefault(na, {"confidence": conf, "keys": {}})
            if na == alias:
                entry["confidence"] = "exact"
            entry["keys"].update(key2kind)
        for na, key2kind in self.norm_index.items():
            entry = merged.setdefault(na, {"confidence": "normalized", "keys": {}})
            for k, v in key2kind.items():
                entry["keys"].setdefault(k, v)
        hits = []
        for na, entry in merged.items():
            start = 0
            while True:
                pos = norm_q.find(na, start)
                if pos < 0:
                    break
                hits.append((pos, pos + len(na),
                             {"confidence": entry["confidence"],
                              "keys": dict(entry["keys"])}))
                start = pos + 1
        # 重叠取更长者，其次 exact 优先、起点靠前者优先
        hits.sort(key=lambda h: (-(h[1] - h[0]),
                                 0 if h[2]["confidence"] == "exact" else 1,
                                 h[0]))
        chosen, used = [], []
        for h in hits:
            s, e = h[0], h[1]
            if any(s < ue and us < e for us, ue in used):
                continue
            chosen.append(h)
            used.append((s, e))
        chosen.sort(key=lambda h: h[0])
        return chosen

    def _pick_stronger(self, key2kind):
        """同名变体裁决：某种别名形式更强（组合全名 > 裸名）且唯一时取它。"""
        if len(key2kind) <= 1:
            return dict(key2kind)
        best_w = max(_KIND_WEIGHT.get(k, 0) for k in key2kind.values())
        best = {key: k for key, k in key2kind.items()
                if _KIND_WEIGHT.get(k, 0) == best_w}
        return best if len(best) == 1 else dict(key2kind)

    def _resolve_fuzzy(self, mention):
        """字符重叠模糊候选；返回 ("resolved", key) / ("ambiguous", keys) / ("none",)"""
        nm = normalize(mention)
        if len(nm) < 2:
            return ("none",)
        scores = {}  # card_key -> (score, kind)
        for alias, key2kind in self.alias_index.items():
            na = normalize(alias)
            if len(na) < 2:
                continue
            sc = _overlap_score(nm, na)
            if sc >= 2 and sc * 2 >= min(len(nm), len(na)):
                for key, kind in key2kind.items():
                    if key not in scores or sc > scores[key][0]:
                        scores[key] = (sc, kind)
        if not scores:
            return ("none",)
        ranked = sorted(scores.items(),
                        key=lambda kv: (-kv[1][0], kv[0]))[: self.top_k]
        best_score = ranked[0][1][0]
        top = {k: v[1] for k, v in ranked if v[0] == best_score}
        top = self._pick_stronger(top)
        if len(top) == 1:
            return "resolved", next(iter(top))
        return "ambiguous", top

    # ---------- 内部：输出结构与 LLM ----------

    def _resolved_item(self, card_key, mention, confidence, source):
        info = self.cards.get(card_key, {})
        name_cn = info.get("name_cn")
        sub = info.get("sub_title_cn")
        if sub and name_cn:
            name_cn = u"%s %s" % (sub, name_cn)
        return {
            "card_id": card_key,
            "mention": mention,
            "name_cn": name_cn,
            "name_en": info.get("name_en"),
            "confidence": confidence,
            "source": source,
        }

    def _ambiguous_item(self, mention, key2kind):
        cands = []
        for key in sorted(key2kind):
            info = self.cards.get(key, {})
            cands.append({"card_id": key,
                          "name_cn": info.get("name_cn"),
                          "name_en": info.get("name_en")})
        return {"mention": mention, "candidates": cands}

    def _call_llm_extract(self, query):
        try:
            names = self.llm_extract(query)
        except Exception as exc:
            print("card_resolver: llm_extract 调用失败，忽略: %s" % exc,
                  file=sys.stderr)
            return []
        if isinstance(names, str):
            names = [names]
        if not isinstance(names, (list, tuple)):
            return []
        return [str(n).strip() for n in names if str(n).strip()][: self.top_k]

    # ---------- 调试 ----------

    def debug_index(self):
        return json.dumps({"cards": len(self.cards),
                           "aliases": len(self.alias_index),
                           "norm_aliases": len(self.norm_index)},
                          ensure_ascii=False)
