# -*- coding: utf-8 -*-
"""Riftbound 规则 RAG agent 模式：有界 planner→工具循环（无框架依赖）。

planner 每步输出一个 JSON 动作 {"tool": ..., "arguments": {...}, "rationale": ...}：
    resolve_cards  {"mentions": [str, ...]}          确定性解析卡名提及
    get_card_rules {"card_id": str, "top_k": int?}   按卡号取关联规则
    search_rules   {"query": str, "top_k": int?}     混合召回规则库（自动含已解析卡扩展，R-CARD 条目并入证据池）
    lookup_rule    {"ref": str}                      按 rule_id / 裸规则号直查
    submit_answer  {"answer": str, "citations": [str]}  唯一终止动作，引用经证据池校验

界限（design D4）：
    - RAG_AGENT_MAX_STEPS 最大步数（默认 4，钳制 1-8）；
    - 重复 (tool, 规范化 arguments) 签名拒绝执行（给出观察，不计无效）；
    - 连续两个无效输出（非 JSON / 未知工具 / 参数畸形）停止进 fallback；
    - planner LLM 调用失败直接进 fallback。
任何失败/耗尽都确定性回退 one-shot 生成（rag_query.generate），绝不把异常抛给用户。
"""
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field

import rag_query
from rag_query import EvidencePool, get_card_rules, lookup_rule, search_rules

TOOL_NAMES = ("resolve_cards", "get_card_rules", "search_rules",
              "lookup_rule", "submit_answer")

DEFAULT_MAX_STEPS = 4
MIN_MAX_STEPS = 1
MAX_MAX_STEPS = 8

EMPTY_RETRIEVAL_ANSWER = (
    "未在规则库中检索到与该问题相关的条目，"
    "请补充章节号（如 716.1）、卡号（如 OGN-131）或换一种问法后重试。"
)

# 答案中的引用标记：[R-CR-716.1] / [R-CARD-OGN-242] 等（不允许空白/嵌套括号）
_RE_CITE = re.compile(r"\[([^\[\]\s]{1,64})\]")

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
_RE_SET_NUMBER = re.compile(r"^([A-Za-z]{2,4})-(\d{3})")


def default_cards_db():
    """cards_bilingual.db 路径（全量卡文来源）；RAG_CARDS_DB_PATH 可覆盖。"""
    return os.environ.get("RAG_CARDS_DB_PATH") or os.path.join(
        _REPO_ROOT, "cards_bilingual.db")


def card_text_rows(cards_db_path, card_ids, limit=2):
    """从 cards_bilingual.db 按卡号取规范效果文本，合成证据行（7 元组形状）。

    合成 rule_id ``R-CARD-<卡号>-TEXT``（与 rules.db 中 R-CARD 裁定条目不冲突），
    卡文放入 proposed_canonical_rule 列（build_context 的"规范规则"位）。
    cards DB 缺失/读取失败时返回 []。
    """
    out = []
    if not cards_db_path or not os.path.exists(cards_db_path):
        return out
    try:
        db = sqlite3.connect(cards_db_path)
        try:
            for card_id in (card_ids or [])[:limit]:
                m = _RE_SET_NUMBER.match(card_id or "")
                if not m:
                    continue
                row = db.execute(
                    "SELECT set_id, number, name_en, name_cn, text_en, text_cn "
                    "FROM cards WHERE UPPER(set_id) = ? AND number = ? "
                    "ORDER BY CASE variant WHEN 'base' THEN 0 ELSE 1 END LIMIT 1",
                    (m.group(1).upper(), m.group(2))).fetchone()
                if not row:
                    continue
                set_id, number, name_en, name_cn, text_en, text_cn = row
                parts = []
                if text_cn:
                    parts.append("中文效果：" + text_cn)
                if text_en:
                    parts.append("英文效果：" + text_en)
                if not parts:
                    continue
                cid = "%s-%s" % ((set_id or m.group(1)).upper(), number)
                topic = "card_text:%s (%s / %s)" % (cid, name_en or "", name_cn or "")
                out.append(("R-CARD-%s-TEXT" % cid, topic, "\n".join(parts),
                            "", "", "", "card_text"))
        finally:
            db.close()
    except Exception as exc:
        print("agent_loop: cards DB 卡文读取失败: %s" % exc, file=sys.stderr)
    return out


def _env_int(name, default):
    try:
        return int(os.environ.get(name, "") or default)
    except (TypeError, ValueError):
        return default


def agent_max_steps():
    """RAG_AGENT_MAX_STEPS：默认 4，钳制到 [1, 8]。"""
    raw = _env_int("RAG_AGENT_MAX_STEPS", DEFAULT_MAX_STEPS)
    return max(MIN_MAX_STEPS, min(MAX_MAX_STEPS, raw))


def call_planner(messages, model_name, timeout, thinking_disabled=False):
    """默认 planner：OpenAI 兼容端点（DeepSeek 等），返回原样文本。"""
    from openai import OpenAI

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY") or os.environ.get("RAG_API_KEY"),
        base_url=os.environ.get("OPENAI_BASE_URL") or os.environ.get("RAG_BASE_URL"),
        timeout=timeout,
    )
    kwargs = {}
    if thinking_disabled:
        kwargs["extra_body"] = {"thinking": {"type": "disabled"}}
    resp = client.chat.completions.create(
        model=model_name, messages=messages, temperature=0.1, **kwargs,
    )
    return resp.choices[0].message.content


@dataclass
class AgentResult:
    """agent 循环的结构化结果（服务端据其装配契约 v2 响应）。"""
    answer: str
    warnings: list = field(default_factory=list)
    sources: list = field(default_factory=list)        # [{"rule_id", "topic"}]
    exhausted: bool = False
    resolved_cards: list = field(default_factory=list)
    unresolved_mentions: list = field(default_factory=list)
    ambiguous_mentions: list = field(default_factory=list)
    trace: list = field(default_factory=list)


def _parse_action(content):
    """把 planner 文本解析成 (tool, arguments)；失败返回 (None, 原因)。"""
    if not isinstance(content, str) or not content.strip():
        return None, "planner 输出为空"
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None, "planner 输出不含 JSON 对象"
    try:
        action = json.loads(text[start:end + 1])
    except ValueError as exc:
        return None, "planner 输出不是合法 JSON: %s" % exc
    if not isinstance(action, dict):
        return None, "planner JSON 不是对象"
    tool = action.get("tool")
    if tool not in TOOL_NAMES:
        return None, "未知工具: %r" % (tool,)
    args = action.get("arguments", {})
    if not isinstance(args, dict):
        return None, "arguments 必须是对象"
    return tool, args


def _validate_args(tool, args):
    """各工具的参数形状校验；畸形返回原因字符串，合法返回 None。"""
    if tool == "resolve_cards":
        mentions = args.get("mentions")
        if (not isinstance(mentions, list) or not mentions
                or any(not isinstance(m, str) or not m.strip() for m in mentions)):
            return "resolve_cards.mentions 必须是非空字符串列表"
    elif tool == "get_card_rules":
        if not isinstance(args.get("card_id"), str) or not args["card_id"].strip():
            return "get_card_rules.card_id 必须是非空字符串"
    elif tool == "search_rules":
        if not isinstance(args.get("query"), str) or not args["query"].strip():
            return "search_rules.query 必须是非空字符串"
    elif tool == "lookup_rule":
        if not isinstance(args.get("ref"), str) or not args["ref"].strip():
            return "lookup_rule.ref 必须是非空字符串"
    elif tool == "submit_answer":
        if not isinstance(args.get("answer"), str) or not args["answer"].strip():
            return "submit_answer.answer 必须是非空字符串"
        citations = args.get("citations", [])
        if (not isinstance(citations, list)
                or any(not isinstance(c, str) for c in citations)):
            return "submit_answer.citations 必须是字符串列表"
    if "top_k" in args and (
            isinstance(args["top_k"], bool)
            or not isinstance(args["top_k"], int)
            or not 1 <= args["top_k"] <= 20):
        return "%s.top_k 必须是 1-20 的整数" % tool
    return None


def _signature(tool, args):
    """(tool, 规范化 arguments) 签名：剔除 rationale 等无关键后做重复检测。"""
    canon = json.dumps(args, sort_keys=True, ensure_ascii=False, default=str)
    return (tool, canon)


def build_system_prompt(resolution):
    """planner 系统提示：工具协议 + 预解析结果摘要 + 行为规则。"""
    lines = [
        "你是《符文战场》规则问答的规划器。每步只输出一个 JSON 动作，不要输出其他文本：",
        '{"tool": "<工具名>", "arguments": {...}, "rationale": "<一句话>"}',
        "",
        "可用工具：",
        '- resolve_cards {"mentions": [str]}：确定性解析卡名提及',
        '- get_card_rules {"card_id": str, "top_k": int?}：取该卡关联规则与规范卡文'
        '（卡文引用 id 形如 R-CARD-<卡号>-TEXT，同为证据池条目）',
        '- search_rules {"query": str, "top_k": int?}：混合检索规则库',
        '- lookup_rule {"ref": str}：按 rule_id（R-CR-716.1 / R-CARD-OGN-242）'
        '或裸规则号（716.1）直查',
        '- submit_answer {"answer": str, "citations": [str]}：提交最终答案（终止）；'
        'answer 中每个 […] 引用和 citations 每条都必须是已检索证据的 rule_id',
        "",
        "规则：只引用证据池中的 rule_id；禁止猜测卡号/规则号；"
        "证据足够时立即用 submit_answer 收尾，不要重复检索。",
        "步数预算很小（通常 3-4 步），推荐节奏：resolve_cards 一次 → "
        "search_rules（一次查询覆盖全部已识别卡片与关键概念）→ submit_answer；"
        "get_card_rules 返回 0 条时下一步立即改用 search_rules，"
        "不要逐卡重复 get_card_rules。",
    ]
    resolved = resolution.get("resolved") or []
    ambiguous = resolution.get("ambiguous") or []
    unresolved = resolution.get("unresolved") or []
    if resolved or ambiguous or unresolved:
        lines.append("")
        lines.append("问题中卡名的预解析结果：")
        for item in resolved:
            lines.append("- 已识别：%s → %s（%s）" % (
                item.get("mention"), item.get("card_id"),
                item.get("name_cn") or item.get("name_en") or ""))
        for item in ambiguous:
            cands = "、".join(c.get("card_id") or "?" for c in
                              (item.get("candidates") or []))
            lines.append("- 歧义：%s（候选：%s）" % (item.get("mention"), cands))
        for mention in unresolved:
            lines.append("- 未识别：%s" % mention)
    return "\n".join(lines)


class AgentRunner:
    """单问题的 agent 循环执行器。

    依赖全部注入，便于离线测试：
        db           sqlite3 连接（rules.db）
        resolver     卡名解析器（CardResolver 或同形桩；None 时解析工具不可用）
        kw_vocab     关键词词表（search_rules 关键词通道）
        vec          callable(text) -> {rule_id: (rank, sim)} | None（向量通道）
        planner      callable(list[dict]) -> str；None 时用 call_planner（需 model_name）
        generate_fn  fallback 生成函数（默认 rag_query.generate）
        model_name   生成/planner 模型名（默认 planner 使用）
        generate_timeout  单次 LLM 调用超时秒数
        max_steps    步数上限；None 时取 agent_max_steps()
        cards_db_path  cards_bilingual.db 路径（卡文注入用；None 时取 default_cards_db()）
        thinking_disabled  本循环所有 LLM 调用附加 thinking=disabled（深思考模型用）
    """

    def __init__(self, *, db, resolver=None, kw_vocab=(), vec=None,
                 planner=None, generate_fn=None, model_name=None,
                 generate_timeout=180.0, max_steps=None, cards_db_path=None,
                 thinking_disabled=False):
        self._db = db
        self._resolver = resolver
        self._cards_db_path = cards_db_path or default_cards_db()
        self._thinking_disabled = thinking_disabled
        self._kw_vocab = kw_vocab
        self._vec = vec
        self._model_name = model_name
        self._generate_timeout = generate_timeout
        if planner is None:
            if not model_name:
                raise ValueError("planner 为 None 时必须提供 model_name")
            def planner(messages):
                return call_planner(messages, model_name, generate_timeout,
                                    thinking_disabled=thinking_disabled)
        self._planner = planner
        self._generate = generate_fn or rag_query.generate
        self._max_steps = agent_max_steps() if max_steps is None else max_steps

    # ---------- 主流程 ----------

    def run(self, query, top_k=6):
        warnings = []
        trace = []
        pool = EvidencePool()
        resolution = self._pre_resolve(query, warnings)
        expansion_cache = {}  # card_id -> 规范文本片段（search 扩展用）

        messages = [
            {"role": "system", "content": build_system_prompt(resolution)},
            {"role": "user", "content": "问题：%s" % query},
        ]
        seen = set()
        consecutive_invalid = 0

        for step in range(1, self._max_steps + 1):
            try:
                content = self._planner(messages)
            except Exception as exc:
                # planner LLM 失败：直接回退，不消耗语义上的"无效输出"计数
                print("agent_loop: planner 调用失败，进入 fallback: %s" % exc,
                      file=sys.stderr)
                trace.append({"step": step, "tool": None, "arguments": None,
                              "ok": False,
                              "summary": "planner 调用失败: %.200s" % exc})
                break
            messages.append({"role": "assistant", "content": content})

            tool, args_or_reason = _parse_action(content)
            if tool is None:
                consecutive_invalid += 1
                trace.append({"step": step, "tool": None, "arguments": None,
                              "ok": False,
                              "summary": "动作无效: %s" % args_or_reason})
                messages.append({"role": "user", "content": json.dumps(
                    {"ok": False, "error": "动作无效：%s" % args_or_reason,
                     "hint": "请只输出一个 JSON 动作对象"},
                    ensure_ascii=False)})
                if consecutive_invalid >= 2:
                    break
                continue
            args = args_or_reason
            reason = _validate_args(tool, args)
            if reason is not None:
                consecutive_invalid += 1
                trace.append({"step": step, "tool": tool, "arguments": args,
                              "ok": False,
                              "summary": "参数畸形: %s" % reason})
                messages.append({"role": "user", "content": json.dumps(
                    {"ok": False, "error": "参数畸形：%s" % reason},
                    ensure_ascii=False)})
                if consecutive_invalid >= 2:
                    break
                continue
            consecutive_invalid = 0

            sig = _signature(tool, args)
            if sig in seen:
                trace.append({"step": step, "tool": tool, "arguments": args,
                              "ok": False,
                              "summary": "重复动作被拒绝：相同工具与参数已执行过"})
                messages.append({"role": "user", "content": json.dumps(
                    {"ok": False, "error": "重复动作已拒绝：相同工具与参数已执行过"},
                    ensure_ascii=False)})
                continue
            seen.add(sig)

            if tool == "submit_answer":
                bad = self._validate_submission(args["answer"],
                                                args.get("citations", []), pool)
                if bad:
                    messages.append({"role": "user", "content": json.dumps(
                        {"ok": False,
                         "error": "引用 %s 不在证据池中，请改用已检索证据的 rule_id"
                                  % bad[0]},
                        ensure_ascii=False)})
                    trace.append({"step": step, "tool": tool,
                                  "arguments": args, "ok": False,
                                  "summary": "citation validation failed"})
                    continue
                trace.append({"step": step, "tool": tool,
                              "arguments": args, "ok": True,
                              "summary": "submitted"})
                return AgentResult(
                    answer=args["answer"].strip(),
                    warnings=warnings,
                    sources=self._cited_sources(args["answer"],
                                                args.get("citations", []), pool),
                    exhausted=False,
                    resolved_cards=resolution["resolved"],
                    unresolved_mentions=resolution["unresolved"],
                    ambiguous_mentions=resolution["ambiguous"],
                    trace=trace,
                )

            rows, observation = self._execute(
                tool, args, pool, resolution, expansion_cache,
                default_top_k=top_k)
            trace.append({"step": step, "tool": tool, "arguments": args,
                          "ok": observation.get("ok", False),
                          "summary": observation.get("summary", "")})
            messages.append({"role": "user", "content": json.dumps(
                observation, ensure_ascii=False)})

        return self._fallback(query, pool, resolution, warnings, trace,
                              expansion_cache, top_k)

    # ---------- 工具执行 ----------

    def _execute(self, tool, args, pool, resolution, expansion_cache,
                 default_top_k):
        """执行检索类工具；返回 (rows, observation)。异常不外抛。"""
        try:
            if tool == "resolve_cards":
                return self._tool_resolve_cards(args["mentions"], resolution)
            if tool == "get_card_rules":
                return self._tool_get_card_rules(
                    args["card_id"].strip(), args.get("top_k") or default_top_k,
                    pool)
            elif tool == "search_rules":
                rows = self._tool_search_rules(
                    args["query"].strip(), args.get("top_k") or default_top_k,
                    pool, resolution, expansion_cache)
            elif tool == "lookup_rule":
                rows = lookup_rule(self._db, args["ref"].strip())
            else:  # pragma: no cover - _parse_action 已限制工具名
                raise ValueError("unsupported tool: %s" % tool)
        except Exception as exc:
            return [], {"ok": False, "error": "%s 执行失败: %s" % (tool, exc),
                        "summary": "error"}
        pool.add(rows)
        return rows, {"ok": True, "rows": len(rows),
                      "preview": [{"rule_id": r[0], "topic": r[1] or ""}
                                  for r in rows[:5]],
                      "summary": "%d rules" % len(rows)}

    def _tool_resolve_cards(self, mentions, resolution):
        if self._resolver is None:
            return [], {"ok": False, "error": "卡名解析器不可用",
                        "summary": "resolver unavailable"}
        out = {"ok": True, "results": [], "summary": ""}
        for mention in mentions:
            outcome = self._resolver.resolve_name(mention)
            self._merge_resolution(resolution, outcome)
            out["results"].append({
                "mention": mention,
                "resolved": [r.get("card_id") for r in
                             outcome.get("resolved", [])],
                "ambiguous": [a.get("mention") for a in
                              outcome.get("ambiguous", [])],
                "unresolved": outcome.get("unresolved", []),
            })
        out["summary"] = "%d mentions resolved/ambiguous/unresolved" % len(mentions)
        return [], out

    def _tool_get_card_rules(self, card_id, top_k, pool):
        """get_card_rules 工具：rules.db 卡链规则 + cards db 规范卡文一并注入。"""
        rows = get_card_rules(self._db, card_id, top_k)
        text_rows = card_text_rows(self._cards_db_path, [card_id], limit=1)
        all_rows = list(rows) + text_rows
        if not all_rows:
            return [], {"ok": False, "rows": 0,
                        "summary": "该卡无卡链规则与卡文",
                        "hint": "改用 search_rules 组合检索"}
        pool.add(all_rows)
        summary = "%d rules" % len(rows)
        if text_rows:
            summary += "（含卡文 %d 条）" % len(text_rows)
        observation = {
            "ok": True, "rows": len(all_rows),
            "preview": [{"rule_id": r[0], "topic": r[1] or ""}
                        for r in all_rows[:5]],
            "summary": summary}
        if not rows:
            # 没有关联规则行（即使有卡文）：明确引导下一步组合检索，
            # 防止 planner 误以为查到了规则、逐卡重复浪费步数
            observation["hint"] = ("本卡无关联规则行（已注入卡文）；"
                                   "下一步请用 search_rules 组合检索")
        return all_rows, observation

    def _tool_search_rules(self, query, top_k, pool, resolution,
                           expansion_cache):
        expansion_texts = []
        for item in (resolution.get("resolved") or [])[:2]:
            card_id = item.get("card_id")
            if not card_id or card_id in expansion_cache:
                text = expansion_cache.get(card_id)
                if text:
                    expansion_texts.append(text)
                continue
            parts = []
            rc_rows = lookup_rule(self._db, "R-CARD-" + str(card_id))
            pool.add(rc_rows)  # R-CARD 裁定条目本身也是证据
            if rc_rows and rc_rows[0][2]:
                parts.append(rc_rows[0][2][:400])
            # 规范卡文（cards db 全量）一并注入证据池并用作检索扩展
            text_rows = card_text_rows(self._cards_db_path, [card_id], limit=1)
            pool.add(text_rows)
            if text_rows and text_rows[0][2]:
                parts.append(text_rows[0][2][:400])
            text = "\n".join(parts)
            expansion_cache[card_id] = text
            if text:
                expansion_texts.append(text)
        return search_rules(self._db, query, top_k,
                            vec=self._vec, kw_vocab=self._kw_vocab,
                            expansion_texts=expansion_texts)

    # ---------- 解析结果合并 ----------

    @staticmethod
    def _merge_resolution(dst, outcome):
        """把一次 resolve/resolve_name 的结果并入全局解析状态（去重、已识别优先）。"""
        resolved_mentions = {r.get("mention") for r in dst["resolved"]}
        for item in outcome.get("resolved", []):
            if item.get("mention") in resolved_mentions:
                continue
            if any(r.get("card_id") == item.get("card_id")
                   and r.get("mention") == item.get("mention")
                   for r in dst["resolved"]):
                continue
            dst["resolved"].append(item)
            resolved_mentions.add(item.get("mention"))
            dst["ambiguous"] = [a for a in dst["ambiguous"]
                                if a.get("mention") != item.get("mention")]
            dst["unresolved"] = [m for m in dst["unresolved"]
                                 if m != item.get("mention")]
        for item in outcome.get("ambiguous", []):
            mention = item.get("mention")
            if (mention in resolved_mentions
                    or any(a.get("mention") == mention for a in dst["ambiguous"])):
                continue
            dst["ambiguous"].append(item)
            dst["unresolved"] = [m for m in dst["unresolved"] if m != mention]
        for mention in outcome.get("unresolved", []):
            if (mention in resolved_mentions
                    or any(a.get("mention") == mention for a in dst["ambiguous"])
                    or mention in dst["unresolved"]):
                continue
            dst["unresolved"].append(mention)

    def _pre_resolve(self, query, warnings):
        resolution = {"resolved": [], "ambiguous": [], "unresolved": []}
        if self._resolver is None:
            return resolution
        try:
            outcome = self._resolver.resolve(query)
        except Exception as exc:
            print("agent_loop: 预解析失败，按无解析继续: %s" % exc, file=sys.stderr)
            warnings.append("卡名解析失败，已按纯规则检索继续")
            return resolution
        self._merge_resolution(resolution, outcome)
        return resolution

    # ---------- 引用校验与来源 ----------

    @staticmethod
    def _extract_cited(answer, citations):
        """答案文本的 […] 标记（保持出现序）+ citations 列表，去重保持顺序。"""
        cited = []
        for token in _RE_CITE.findall(answer or ""):
            token = token.strip()
            if token and token not in cited:
                cited.append(token)
        for token in citations or []:
            token = token.strip()
            if token and token not in cited:
                cited.append(token)
        return cited

    def _validate_submission(self, answer, citations, pool):
        pool_ids = set(pool.rule_ids)
        return [c for c in self._extract_cited(answer, citations)
                if c not in pool_ids]

    def _cited_sources(self, answer, citations, pool):
        topics = {r[0]: (r[1] or "") for r in pool.rows()}
        return [{"rule_id": c, "topic": topics.get(c, "")}
                for c in self._extract_cited(answer, citations)]

    # ---------- 确定性回退 ----------

    def _fallback(self, query, pool, resolution, warnings, trace,
                  expansion_cache, top_k):
        if len(pool) == 0:
            # 确定性兜底检索：planner 预算可能浪费在无命中的卡查上
            # （如 get_card_rules 0 条），判空前保证做过一次混合检索，
            # 最坏退化为 oneshot 质量而不是空答。
            try:
                _rows, observation = self._execute(
                    "search_rules", {"query": query}, pool, resolution,
                    expansion_cache, default_top_k=top_k)
            except Exception as exc:  # 兜底检索也不外抛
                observation = {"ok": False, "summary": "fallback search error: %s" % exc}
            trace.append({"step": "fallback", "tool": "search_rules",
                          "arguments": {"query": query},
                          "ok": observation.get("ok", False),
                          "summary": observation.get("summary", "")})
        if len(pool) == 0:
            warnings.append("检索结果为空")
            return AgentResult(
                answer=EMPTY_RETRIEVAL_ANSWER,
                warnings=warnings,
                sources=[],
                exhausted=True,
                resolved_cards=resolution["resolved"],
                unresolved_mentions=resolution["unresolved"],
                ambiguous_mentions=resolution["ambiguous"],
                trace=trace,
            )
        rows = pool.rows()
        gen_kwargs = ({"thinking_disabled": True}
                      if self._thinking_disabled else {})
        answer, _ = self._generate(query, rows, self._model_name,
                                   timeout=self._generate_timeout,
                                   **gen_kwargs)
        return AgentResult(
            answer=answer,
            warnings=warnings,
            sources=[{"rule_id": r[0], "topic": r[1] or ""} for r in rows],
            exhausted=True,
            resolved_cards=resolution["resolved"],
            unresolved_mentions=resolution["unresolved"],
            ambiguous_mentions=resolution["ambiguous"],
            trace=trace,
        )
