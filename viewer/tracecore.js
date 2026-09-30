/*
 * tracecore.js — rifttrace/1 纯解析与校验逻辑（无 DOM 依赖）。
 * 浏览器：挂到 window.TraceCore；Node：module.exports。
 * 只消费 trace 文本，绝不 import 引擎代码；缺失数据一律返回 null，由 UI 显示「未知」。
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) { module.exports = factory(); }
  else { root.TraceCore = factory(); }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var KNOWN_SCHEMA_MAJOR = 1;

  /* ---------- 解析 ---------- */

  function parseTrace(text, sourceName) {
    var records = [];
    var parseErrors = [];
    var lines = String(text == null ? '' : text).split(/\r\n|\r|\n/);
    for (var i = 0; i < lines.length; i++) {
      var raw = lines[i];
      if (!raw || !raw.trim()) continue;
      try {
        records.push({ rec: JSON.parse(raw), line: i + 1 });
      } catch (e) {
        parseErrors.push({ line: i + 1, message: String(e && e.message ? e.message : e) });
      }
    }
    var parsed = {
      name: sourceName || '(未命名)',
      records: records,
      parseErrors: parseErrors,
      header: null, footer: null,
      decisions: [], events: [], snapshots: [], others: []
    };
    for (var j = 0; j < records.length; j++) {
      var r = records[j], t = r.rec && r.rec.type;
      if (t === 'header' && !parsed.header) parsed.header = r;
      else if (t === 'header') parsed.others.push(r);
      else if (t === 'footer') { if (!parsed.footer) parsed.footer = r; else parsed.others.push(r); }
      else if (t === 'decision') parsed.decisions.push(r);
      else if (t === 'event') parsed.events.push(r);
      else if (t === 'snapshot') parsed.snapshots.push(r);
      else parsed.others.push(r);
    }
    // 按文件顺序重新排序各类型列表（防御无序文件）
    var byLine = function (a, b) { return a.line - b.line; };
    parsed.decisions.sort(byLine);
    parsed.events.sort(byLine);
    parsed.snapshots.sort(byLine);
    return parsed;
  }

  /* ---------- 校验（加载即复验） ---------- */

  function schemaMajor(schemaVersion) {
    var m = /^rifttrace\/(\d+)$/.exec(String(schemaVersion || ''));
    return m ? parseInt(m[1], 10) : null;
  }

  function validateTrace(parsed) {
    var errors = [];
    var warnings = [];
    var records = parsed.records;

    function err(code, msg) { errors.push({ code: code, message: msg }); }
    function warn(code, msg) { warnings.push({ code: code, message: msg }); }

    if (records.length === 0) {
      err('EMPTY', '文件不含任何可解析记录');
      return { ok: false, errors: errors, warnings: warnings };
    }
    for (var pe = 0; pe < parsed.parseErrors.length; pe++) {
      var p = parsed.parseErrors[pe];
      err('PARSE', '第 ' + p.line + ' 行 JSON 解析失败：' + p.message);
    }

    // header/footer 存在与位置
    if (!parsed.header) err('HEADER_MISSING', '缺少 header 记录');
    else if (records[0] !== parsed.header) err('HEADER_POS', 'header 不是首条记录（line ' + parsed.header.line + '）');
    if (!parsed.footer) err('FOOTER_MISSING', '缺少 footer 记录');
    else if (records[records.length - 1] !== parsed.footer) err('FOOTER_POS', 'footer 不是末条记录（line ' + parsed.footer.line + '）');

    // schema_version 主版本兼容
    var header = parsed.header ? parsed.header.rec : null;
    if (header) {
      var major = schemaMajor(header.schema_version);
      if (major == null) err('SCHEMA_MISSING', 'header.schema_version 缺失或格式非法：' + JSON.stringify(header.schema_version));
      else if (major !== KNOWN_SCHEMA_MAJOR) {
        err('SCHEMA_MAJOR', '未知 schema 主版本 rifttrace/' + major + '（本回放器仅支持 rifttrace/' + KNOWN_SCHEMA_MAJOR + '），拒绝读取');
      }
    }

    // match_id 一致性
    if (header && header.match_id != null) {
      var mism = 0;
      for (var mi = 0; mi < records.length; mi++) {
        var rec = records[mi].rec;
        if (rec && rec.match_id != null && rec.match_id !== header.match_id) mism++;
      }
      if (mism > 0) err('MATCH_ID', '存在 ' + mism + ' 条 match_id 与 header 不一致的记录');
    }

    // event_seq 严格递增（按文件顺序）
    var events = parsed.events;
    for (var s = 1; s < events.length; s++) {
      var prev = events[s - 1].rec.event_seq, cur = events[s].rec.event_seq;
      if (!(typeof prev === 'number' && typeof cur === 'number' && cur > prev)) {
        err('EVENT_SEQ', 'event_seq 未严格递增：line ' + events[s - 1].line + ' seq=' + JSON.stringify(prev) +
          ' → line ' + events[s].line + ' seq=' + JSON.stringify(cur));
        break;
      }
    }

    // hash 链连续：引擎按决策步整块记录 before/after（同块内事件 hash 相同），
    // 折叠相邻相同的 (before,after) 块后，块间必须满足 下一块.before == 上一块.after。
    var blocks = [];
    var missingHash = 0;
    for (var e = 0; e < events.length; e++) {
      var ev = events[e].rec;
      var b = ev.before_state_hash, a = ev.after_state_hash;
      if (typeof b !== 'string' || !b || typeof a !== 'string' || !a) {
        if (missingHash === 0) err('HASH_MISSING', '事件缺少 before/after_state_hash：event_seq=' + ev.event_seq + '（line ' + events[e].line + '）');
        missingHash++;
        continue;
      }
      var last = blocks[blocks.length - 1];
      if (!last || last.before !== b || last.after !== a) {
        blocks.push({ before: b, after: a, seq: ev.event_seq });
      }
    }
    if (missingHash > 1) err('HASH_MISSING', '共 ' + missingHash + ' 条事件缺少 before/after_state_hash');
    for (var c = 1; c < blocks.length; c++) {
      if (blocks[c].before !== blocks[c - 1].after) {
        err('HASH_CHAIN', 'hash 链断裂：event_seq=' + blocks[c].seq + ' 的 before(' + shortHash(blocks[c].before) +
          ') != 前一块 after(' + shortHash(blocks[c - 1].after) + ')');
      }
    }

    // footer 完整性与终局 hash
    var footer = parsed.footer ? parsed.footer.rec : null;
    if (footer) {
      var tc = footer.trace_completeness;
      if (!tc || typeof tc !== 'object') {
        err('COMPLETENESS_MISSING', 'footer 缺少 trace_completeness');
      } else {
        if (tc.ok !== true) err('COMPLETENESS_FLAG', 'footer.trace_completeness.ok != true：' + JSON.stringify(tc));
        if (tc.expected_events !== tc.written_events) {
          err('COMPLETENESS_COUNT', 'trace_completeness expected(' + tc.expected_events + ') != written(' + tc.written_events + ')');
        }
        if (tc.written_events !== events.length) {
          err('COMPLETENESS_ACTUAL', 'trace_completeness.written_events(' + tc.written_events + ') != 实际事件数(' + events.length + ')');
        }
      }
      if (typeof footer.final_state_hash === 'string' && footer.final_state_hash && blocks.length > 0) {
        var tail = blocks[blocks.length - 1].after;
        if (tail !== footer.final_state_hash) {
          warn('FINAL_HASH', '末事件块 after(' + shortHash(tail) + ') 与 footer.final_state_hash(' + shortHash(footer.final_state_hash) + ') 不一致');
        }
      }
    }

    // 每条 decision：chosen ∈ legal
    for (var d = 0; d < parsed.decisions.length; d++) {
      var dec = parsed.decisions[d].rec;
      var legal = dec.legal_action_ids;
      if (!Array.isArray(legal)) {
        err('LEGAL_MISSING', 'step ' + dec.step_id + ' 的 decision 缺少 legal_action_ids');
        continue;
      }
      var found = false;
      for (var li = 0; li < legal.length; li++) { if (legal[li] === dec.chosen_action_id) { found = true; break; } }
      if (!found) {
        err('CHOSEN_NOT_LEGAL', 'step ' + dec.step_id + '：chosen_action_id 不在 legal_action_ids 中（line ' + parsed.decisions[d].line + '）');
      }
    }

    if (parsed.snapshots.length === 0) {
      warn('NO_SNAPSHOT', '本局无 snapshot 记录：场面无法复原，将以「未知」展示');
    }
    return { ok: errors.length === 0, errors: errors, warnings: warnings };
  }

  function shortHash(h) { return typeof h === 'string' ? h.slice(0, 12) : String(h); }

  /* ---------- 对局索引摘要（§3.5） ---------- */

  function indexSummary(parsed, validation) {
    var header = parsed.header ? parsed.header.rec : {};
    var footer = parsed.footer ? parsed.footer.rec : {};
    var res = footer.result || {};
    var len = footer.length || {};
    var invalid = footer.invalid_action_count;
    var term = res.termination_reason != null ? String(res.termination_reason) : null;
    var anomalies = [];
    if (typeof invalid === 'number' && invalid > 0) anomalies.push({ label: '非法动作×' + invalid, severity: 'red' });
    if (term && /truncated/i.test(term)) anomalies.push({ label: 'TRUNCATED', severity: 'red' });
    if (term && /burnout/i.test(term)) anomalies.push({ label: 'BURNOUT', severity: 'red' });
    if (validation && !validation.ok) anomalies.push({ label: '校验失败', severity: 'red' });
    if (validation && validation.ok === false) { /* 已在上方标记 */ }
    return {
      matchId: header.match_id != null ? String(header.match_id) : null,
      seed: header.seed != null ? header.seed : null,
      policies: Array.isArray(header.policy_ids) ? header.policy_ids.slice() : null,
      engineVersion: header.engine_version != null ? String(header.engine_version) : null,
      traceLevel: header.trace_level != null ? String(header.trace_level) : null,
      visibility: header.visibility != null ? String(header.visibility) : null,
      winner: res.winner != null ? res.winner : null,
      termination: term,
      modalWinner: res.modal_winner === true,
      steps: len.decision_steps != null ? len.decision_steps : null,
      turns: len.turns != null ? len.turns : null,
      eventCount: len.events != null ? len.events : events_len(parsed),
      invalid: typeof invalid === 'number' ? invalid : null,
      anomalies: anomalies
    };
  }
  function events_len(parsed) { return parsed.events.length; }

  /* ---------- 帧组织 ---------- */

  function buildFrames(parsed) {
    var map = {};
    function frame(stepId) {
      var k = String(stepId);
      if (!map[k]) map[k] = { stepId: stepId, decision: null, events: [], snapshot: null };
      return map[k];
    }
    var i;
    for (i = 0; i < parsed.decisions.length; i++) frame(parsed.decisions[i].rec.step_id).decision = parsed.decisions[i].rec;
    for (i = 0; i < parsed.events.length; i++) frame(parsed.events[i].rec.step_id).events.push(parsed.events[i].rec);
    for (i = 0; i < parsed.snapshots.length; i++) {
      var snap = parsed.snapshots[i].rec;
      frame(snap.step_id).snapshot = snap;
    }
    var frames = [];
    for (var k in map) if (Object.prototype.hasOwnProperty.call(map, k)) frames.push(map[k]);
    frames.sort(function (a, b) { return a.stepId - b.stepId; });
    for (i = 0; i < frames.length; i++) {
      frames[i].events.sort(function (a, b) { return (a.event_seq || 0) - (b.event_seq || 0); });
    }
    return frames;
  }

  /* ---------- 锚点（§3.2 跳转） ---------- */

  function buildAnchors(parsed) {
    var turnStarts = [];
    var scores = [];
    var combats = [];
    var wins = [];
    var seen = {};
    function push(list, seq, stepId, tag) {
      var key = list === turnStarts ? 't' + stepId : null;
      if (key && seen[key]) return;
      if (key) seen[key] = true;
      list.push({ stepId: stepId, seq: seq, tag: tag });
    }
    for (var i = 0; i < parsed.events.length; i++) {
      var ev = parsed.events[i].rec;
      var pp = ev.public_payload || {};
      if (ev.event_type === 'PHASE_ENTER' && pp.phase === 'awaken' && pp.turn != null) {
        push(turnStarts, ev.event_seq, ev.step_id, '回合' + pp.turn);
      } else if (ev.event_type === 'SCORE') push(scores, ev.event_seq, ev.step_id, '得分');
      else if (ev.event_type === 'COMBAT_START') push(combats, ev.event_seq, ev.step_id, '战斗开始');
      else if (ev.event_type === 'WIN') push(wins, ev.event_seq, ev.step_id, '胜负');
    }
    return { turnStarts: turnStarts, scores: scores, combats: combats, wins: wins };
  }

  /* ---------- 视图派生（隐藏信息隔离核心） ----------
   * P0/P1：使用对应玩家的引擎公开观察（含其 self 手牌）。
   * OBSERVER：仅取 view["0"] 的公共结构，self 侧**重建一个不含 hand/hidden 字段的座位对象**，
   *           hand 内容从未被引用、复制或渲染；opponent 侧本就只有公开计数。
   * PRIVILEGED：不接触 public_view 之外的特权字段；快照无 privileged_state_ref 时标注无数据。
   */
  function normSeat(p, exposeHand) {
    if (!p || typeof p !== 'object') return null;
    return {
      seat: p.seat != null ? p.seat : null,
      handCount: p.hand_count != null ? p.hand_count : null,
      mainDeckCount: p.main_deck_count != null ? p.main_deck_count : null,
      runeDeckCount: p.rune_deck_count != null ? p.rune_deck_count : null,
      trash: Array.isArray(p.trash) ? p.trash : null,
      banish: Array.isArray(p.banish) ? p.banish : null,
      runeEnergy: p.rune_energy != null ? p.rune_energy : null,
      runePower: (p.rune_power && typeof p.rune_power === 'object') ? p.rune_power : null,
      score: p.score != null ? p.score : null,
      scoreMarks: (p.score_marks && typeof p.score_marks === 'object') ? p.score_marks : null,
      heroZone: Array.isArray(p.hero_zone) ? p.hero_zone : null,
      legendZone: Array.isArray(p.legend_zone) ? p.legend_zone : null,
      // 本方待命内容仅属 self 私有（见 observation.self_private）；其余视角恒为 null。
      hidden: exposeHand === true && Array.isArray(p.hidden) ? p.hidden : null,
      // 只有显式 exposeHand（P0/P1 视角看自己）才引用 hand；OBSERVER/PRIVILEGED 恒为 null。
      hand: exposeHand === true && Array.isArray(p.hand) ? p.hand : null,
      handExposed: exposeHand === true && Array.isArray(p.hand)
    };
  }

  function deriveView(snapshot, perspective) {
    if (!snapshot || typeof snapshot !== 'object') return null;
    var views = snapshot.public_view_by_player;
    if (!views || typeof views !== 'object') return null;
    var key = perspective === 'P1' ? '1' : '0';
    var v = views[key];
    if (!v || typeof v !== 'object') return null;
    var exposeHand = (perspective === 'P0' && key === '0') || (perspective === 'P1' && key === '1');
    var seats = [normSeat(v.self, exposeHand), normSeat(v.opponent, false)];
    seats.sort(function (a, b) { return ((a && a.seat != null) ? a.seat : 0) - ((b && b.seat != null) ? b.seat : 0); });
    return {
      stepId: snapshot.step_id != null ? snapshot.step_id : null,
      stateHash: snapshot.state_hash || null,
      privilegedStateRef: snapshot.privileged_state_ref != null ? snapshot.privileged_state_ref : null,
      turn: v.turn || null,
      turnState: v.turn_state || null,
      ended: v.ended != null ? v.ended : null,
      winner: v.winner != null ? v.winner : null,
      termination: v.termination != null ? v.termination : null,
      priority: v.priority != null ? v.priority : null,
      focus: v.focus != null ? v.focus : null,
      showdownBf: v.showdown_bf != null ? v.showdown_bf : null,
      board: Array.isArray(v.board) ? v.board : null,
      bases: Array.isArray(v.bases) ? v.bases : null,
      seats: seats,
      chain: Array.isArray(v.chain) ? v.chain : null,
      request: v.request != null ? v.request : null
    };
  }

  /* ---------- 公开状态字段级 diff（§3.2，new/removed/changed 三型） ---------- */

  function flatten(obj, prefix, out) {
    if (obj == null || typeof obj !== 'object') { out[prefix] = obj == null ? null : obj; return; }
    var keys = Object.keys(obj);
    if (keys.length === 0) { out[prefix] = Array.isArray(obj) ? [] : {}; return; }
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i];
      flatten(obj[k], prefix ? prefix + '.' + k : k, out);
    }
  }

  function diffViews(before, after) {
    if (!before || !after) return [];
    var fa = {}, fb = {};
    flatten(before, '', fa);
    flatten(after, '', fb);
    var out = [];
    var k;
    for (k in fa) {
      if (!Object.prototype.hasOwnProperty.call(fb, k)) {
        out.push({ kind: 'removed', path: k, before: fa[k], after: undefined });
      } else if (!leafEqual(fa[k], fb[k])) {
        out.push({ kind: 'changed', path: k, before: fa[k], after: fb[k] });
      }
    }
    for (k in fb) {
      if (!Object.prototype.hasOwnProperty.call(fa, k)) {
        out.push({ kind: 'new', path: k, before: undefined, after: fb[k] });
      }
    }
    out.sort(function (a, b) { return a.path < b.path ? -1 : a.path > b.path ? 1 : 0; });
    return out;
  }

  function leafEqual(a, b) {
    if (a === b) return true;
    if (a != null && b != null && typeof a === 'object' && typeof b === 'object') {
      return JSON.stringify(a) === JSON.stringify(b);
    }
    return false;
  }

  /* ---------- Action 描述（§3.3 合法动作解码） ---------- */

  var KIND_CN = {
    end_main: '结束主阶段', play_card: '打出卡牌', activate_ability: '激活技能',
    std_move: '标准移动', hide: '待命', pass: '让过', resolve_choice: '选择回答',
    assign_damage: '伤害分配', concede: '认输', execute_reaction: '执行反应'
  };

  function parseAction(jsonStr) {
    if (typeof jsonStr !== 'string') return null;
    try { return JSON.parse(jsonStr); } catch (e) { return null; }
  }

  function describeAction(jsonStr) {
    var a = parseAction(jsonStr);
    if (!a || typeof a !== 'object') {
      return { ok: false, brief: '未知（动作 JSON 无法解析）', action: null };
    }
    var parts = [];
    parts.push('P' + (a.actor != null ? a.actor : '?'));
    var kindCn = KIND_CN[a.kind] || ('未知动作[' + (a.kind == null ? '?' : a.kind) + ']');
    parts.push(kindCn);
    var p = a.params || {};
    if (a.kind === 'play_card' && p.location != null) parts.push('→ ' + fmtLocation(p.location));
    if (a.kind === 'std_move' && p.to != null) parts.push('→ ' + fmtLocation(p.to));
    if (a.kind === 'hide' && p.battlefield != null) parts.push('→ 战场 ' + JSON.stringify(p.battlefield));
    if (a.kind === 'resolve_choice') {
      if (Array.isArray(p.set_aside)) parts.push('（置牌 ' + p.set_aside.length + ' 张）');
      else if (p.choice != null) parts.push('（选择 ' + abbrev(p.choice) + '）');
      else if (p.targets != null) parts.push('（目标 ' + abbrev(p.targets) + '）');
      else if (p.order != null) parts.push('（顺序 ' + abbrev(p.order) + '）');
    }
    if (a.kind === 'assign_damage') {
      var assign = p.assignments || p.assign || null;
      if (assign) parts.push('（' + abbrev(assign) + '）');
    }
    if (a.kind === 'activate_ability' && p.ability_id != null) parts.push('「' + a.ability_id + '」');
    if (p.in_reaction === true) parts.push('[反应]');
    if (a.source_uid != null) parts.push('uid:' + a.source_uid);
    return { ok: true, brief: parts.join(' '), action: a };
  }

  function fmtLocation(loc) {
    if (Array.isArray(loc)) return loc.join(' ');
    return abbrev(loc);
  }

  /* ---------- 事件摘要 ---------- */

  var EVENT_CN = {
    SETUP: '起手设置', MULLIGAN: '调度', PHASE_ENTER: '进入阶段', READY: '重置', CHANNEL: '引导符文',
    DRAW: '抽牌', BURNOUT: '燃尽', POOL_CLEAR: '符文池清空', PLAY_STEP: '打出步骤', PAID: '支付费用',
    FINALIZE: '定稿', EXECUTE: '执行', PASS: '让过', RESOLVE: '结算', TRIGGER_QUEUED: '触发入队',
    COUNTERED: '被反击', MOVE: '移动', RECALL: '召回', CONTEST: '争夺', SHOWDOWN_START: '对决开始',
    SHOWDOWN_END: '对决结束', COMBAT_START: '战斗开始', COMBAT_DAMAGE_ASSIGNED: '战斗伤害分配',
    COMBAT_DAMAGE: '战斗伤害', COMBAT_END: '战斗结束', SCORE: '得分', WIN: '胜利',
    CLEANUP_START: '清理开始', CLEANUP_ITEM: '清理项', KILL: '击杀', DAMAGE: '伤害', HEAL: '治疗',
    BUFF: '增益', ATTACH: '贴附', DETACH: '卸下', RETURN: '返回', DISCARD: '弃牌', RECYCLE: '回收',
    BANISH: '放逐', CONCEDE: '认输', END_TURN: '回合结束', ERROR: '错误'
  };

  function eventSummary(ev) {
    if (!ev || typeof ev !== 'object') return { typeCn: '未知', known: false, payloadText: '' };
    var cn = EVENT_CN[ev.event_type];
    var payloadText = '';
    var pp = ev.public_payload;
    if (pp && typeof pp === 'object') {
      var keys = Object.keys(pp).slice(0, 4);
      var pairs = [];
      for (var i = 0; i < keys.length; i++) {
        var k = keys[i];
        pairs.push(k + '=' + abbrev(pp[k]));
      }
      payloadText = pairs.join(' ');
      if (Object.keys(pp).length > 4) payloadText += ' …';
    }
    return { typeCn: cn || (ev.event_type + '（未知事件）'), known: !!cn, payloadText: payloadText };
  }

  function abbrev(v, maxLen) {
    var s = typeof v === 'string' ? v : JSON.stringify(v);
    if (s == null) s = String(v);
    var cap = maxLen || 60;
    return s.length > cap ? s.slice(0, cap - 1) + '…' : s;
  }

  return {
    KNOWN_SCHEMA_MAJOR: KNOWN_SCHEMA_MAJOR,
    parseTrace: parseTrace,
    validateTrace: validateTrace,
    indexSummary: indexSummary,
    buildFrames: buildFrames,
    buildAnchors: buildAnchors,
    deriveView: deriveView,
    diffViews: diffViews,
    describeAction: describeAction,
    eventSummary: eventSummary,
    schemaMajor: schemaMajor,
    abbrev: abbrev,
    EVENT_CN: EVENT_CN,
    KIND_CN: KIND_CN
  };
});
