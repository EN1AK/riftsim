/*
 * app.js — 只读回放器 UI 层。所有数据来自 TraceCore 派生结果；不引入引擎代码。
 * 隐藏信息纪律：OBSERVER / PRIVILEGED 档位消费的视图对象中 hand 字段恒为 null
 * （TraceCore.deriveView 重建座位对象，从未引用手牌内容），本文件无法渲染其内容。
 */
(function () {
  'use strict';
  var TC = window.TraceCore;

  var PHASE_CN = {
    setup: '设置', awaken: '唤醒', begin: '开始', channel: '引导', draw: '抽牌',
    main: '主阶段', combat: '战斗', ending: '结束阶段'
  };
  var REQUEST_CN = {
    mulligan: '调度', main_action: '主阶段行动', reaction_execute: 'REACTION 执行窗',
    showdown_focus: '对决焦点', choose_targets: '选择目标', choose_location: '选择位置',
    choose_mode: '选择模式', assign_damage: '战斗分配（伤害分配）', choose_battlefield_next: '选择下一个战场',
    order_triggers: '触发排序', order_replacements: '替换排序', scout_keep: '洞察去留', pass_priority: '让过优先权'
  };

  var state = {
    matches: [],          // {name, parsed, validation, summary, frames, anchors}
    currentIdx: -1,
    frameIdx: 0,
    perspective: 'OBSERVER',
    privAuthorized: false,
    playing: false,
    timer: null
  };

  /* ---------- 小工具 ---------- */
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function unk(v, fmt) {
    if (v == null) return el('span', 'unknown', '未知');
    return el('span', null, fmt ? fmt(v) : String(v));
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }
  function $(id) { return document.getElementById(id); }
  function shortHash(h) { return typeof h === 'string' ? h.slice(0, 12) + '…' : '未知'; }
  function jsonText(v) { try { return JSON.stringify(v); } catch (e) { return String(v); } }

  /* ---------- trace 加载 ---------- */
  function addTraceText(name, text) {
    var parsed = TC.parseTrace(text, name);
    var validation = TC.validateTrace(parsed);
    var summary = TC.indexSummary(parsed, validation);
    var frames = TC.buildFrames(parsed);
    var anchors = TC.buildAnchors(parsed);
    var existing = -1;
    for (var i = 0; i < state.matches.length; i++) {
      if (state.matches[i].name === name) { existing = i; break; }
    }
    var entry = { name: name, parsed: parsed, validation: validation, summary: summary, frames: frames, anchors: anchors };
    if (existing >= 0) state.matches[existing] = entry; else state.matches.push(entry);
    renderIndex();
    if (state.currentIdx < 0 || existing === state.currentIdx) {
      selectMatch(existing >= 0 ? existing : state.matches.length - 1);
    }
  }

  function loadFiles(fileList) {
    var files = Array.prototype.slice.call(fileList || []);
    if (!files.length) return;
    files.forEach(function (f) {
      var reader = new FileReader();
      reader.onload = function () { addTraceText(f.name, String(reader.result || '')); };
      reader.onerror = function () { showTopError([{ code: 'IO', message: '读取文件失败：' + f.name }]); };
      reader.readAsText(f, 'utf-8');
    });
  }

  /* ---------- 顶部错误/警告（§3.6 失败禁止播放） ---------- */
  function showTopError(errors, prefix) {
    var box = $('errorBox');
    clear(box);
    if (!errors || !errors.length) return;
    var div = el('div', 'banner-error');
    div.appendChild(el('b', null, (prefix || '校验失败，已禁止播放（§3.6）：')));
    var ul = el('ul');
    errors.slice(0, 50).forEach(function (e) {
      ul.appendChild(el('li', null, '[' + e.code + '] ' + e.message));
    });
    if (errors.length > 50) ul.appendChild(el('li', null, '…另有 ' + (errors.length - 50) + ' 条'));
    div.appendChild(ul);
    box.appendChild(div);
  }
  function showTopWarn(warnings) {
    var box = $('warnBox');
    clear(box);
    if (!warnings || !warnings.length) return;
    var div = el('div', 'banner-warn');
    div.appendChild(el('b', null, '警告（不阻断回放）：'));
    var ul = el('ul');
    warnings.forEach(function (w) { ul.appendChild(el('li', null, '[' + w.code + '] ' + w.message)); });
    div.appendChild(ul);
    box.appendChild(div);
  }

  /* ---------- 对局索引表 ---------- */
  function renderIndex() {
    var wrap = $('indexTableWrap');
    clear(wrap);
    if (!state.matches.length) {
      wrap.appendChild(el('span', 'unknown', '尚未加载 trace。'));
      return;
    }
    var table = el('table', 'index');
    var thead = el('thead');
    var tr = el('tr');
    ['文件', 'match_id', 'seed', 'policies', '胜负', '终止原因', '步/回合/事件', '非法动作', '异常', '引擎版本'].forEach(function (h) {
      tr.appendChild(el('th', null, h));
    });
    thead.appendChild(tr);
    table.appendChild(thead);
    var tbody = el('tbody');
    state.matches.forEach(function (m, idx) {
      var s = m.summary;
      var row = el('tr', 'clickable');
      if (idx === state.currentIdx) row.classList.add('current');
      row.onclick = function () { selectMatch(idx); };
      row.appendChild(el('td', null, m.name));
      row.appendChild(el('td', null, s.matchId != null ? s.matchId : '未知'));
      row.appendChild(el('td', null, s.seed != null ? String(s.seed) : '未知'));
      row.appendChild(el('td', null, s.policies ? s.policies.join(' / ') : '未知'));
      var wtd = el('td');
      if (s.winner != null) wtd.textContent = 'P' + s.winner + ' 胜';
      else if (s.termination != null) wtd.appendChild(unk(null));
      else wtd.appendChild(unk(null));
      row.appendChild(wtd);
      row.appendChild(el('td', null, s.termination != null ? s.termination : '未知'));
      row.appendChild(el('td', null,
        (s.steps != null ? s.steps : '?') + ' / ' + (s.turns != null ? s.turns : '?') + ' / ' + (s.eventCount != null ? s.eventCount : '?')));
      var itd = el('td', null, s.invalid != null ? String(s.invalid) : '未知');
      row.appendChild(itd);
      var atd = el('td');
      if (s.anomalies.length) {
        s.anomalies.forEach(function (a) { atd.appendChild(el('span', 'tag ' + a.severity, a.label)); });
      } else {
        atd.appendChild(el('span', 'tag green', '正常'));
      }
      row.appendChild(atd);
      row.appendChild(el('td', null, s.engineVersion != null ? s.engineVersion : '未知'));
      tbody.appendChild(row);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
  }

  /* ---------- 选择对局 ---------- */
  function current() { return state.matches[state.currentIdx] || null; }

  function selectMatch(idx) {
    stopPlay();
    state.currentIdx = idx;
    state.frameIdx = 0;
    renderIndex();
    var m = current();
    showTopError(m && !m.validation.ok ? m.validation.errors : null);
    showTopWarn(m ? m.validation.warnings : null);
    var replay = $('replaySection');
    if (!m) { replay.classList.add('hidden'); return; }
    if (!m.validation.ok) {
      replay.classList.add('hidden');   // 校验失败：禁止播放
      return;
    }
    replay.classList.remove('hidden');
    buildAnchorOptions(m);
    var slider = $('timelineSlider');
    slider.max = String(Math.max(0, m.frames.length - 1));
    slider.value = '0';
    var h = m.parsed.header ? m.parsed.header.rec : {};
    var meta = $('matchMeta');
    clear(meta);
    meta.textContent = (h.match_id || '?') + ' · seed=' + (h.seed != null ? h.seed : '?') +
      ' · schema=' + (h.schema_version || '?') + ' · ' + (h.trace_level || '?') + ' 级';
    renderFrame();
  }

  function buildAnchorOptions(m) {
    var sel = $('anchorSelect');
    clear(sel);
    sel.appendChild(el('option', null, '（回合/战斗/得分/终局锚点）')).value = '';
    var a = m.anchors;
    function idxOfStep(stepId) {
      for (var i = 0; i < m.frames.length; i++) if (m.frames[i].stepId >= stepId) return i;
      return m.frames.length - 1;
    }
    a.turnStarts.forEach(function (t) {
      var o = el('option', null, '回合 ' + (t.tag || '') + '（step ' + t.stepId + '）');
      o.value = String(idxOfStep(t.stepId));
      sel.appendChild(o);
    });
    a.combats.forEach(function (t, i) {
      var o = el('option', null, 'COMBAT_START #' + (i + 1) + '（step ' + t.stepId + '）');
      o.value = String(idxOfStep(t.stepId));
      sel.appendChild(o);
    });
    a.scores.forEach(function (t, i) {
      var o = el('option', null, 'SCORE #' + (i + 1) + '（step ' + t.stepId + '）');
      o.value = String(idxOfStep(t.stepId));
      sel.appendChild(o);
    });
    a.wins.forEach(function (t) {
      var o = el('option', null, 'WIN（step ' + t.stepId + '）');
      o.value = String(idxOfStep(t.stepId));
      sel.appendChild(o);
    });
    if (m.frames.length) {
      var end = el('option', null, '终局（最后一帧）');
      end.value = String(m.frames.length - 1);
      sel.appendChild(end);
    }
  }

  /* ---------- 帧渲染 ---------- */
  function renderFrame() {
    var m = current();
    if (!m) return;
    var frames = m.frames;
    if (!frames.length) return;
    state.frameIdx = Math.max(0, Math.min(state.frameIdx, frames.length - 1));
    var frame = frames[state.frameIdx];
    var view = TC.deriveView(frame.snapshot, state.perspective === 'PRIVILEGED' ? 'OBSERVER' : state.perspective);

    $('timelineSlider').value = String(state.frameIdx);
    renderFrameInfo(m, frame, view);
    renderBanner(frame, view);
    renderArena(view);
    renderEvents(frame);
    renderDecision(m, frame);
    renderDiff(m, view);
    renderFooter(m);
  }

  function renderFrameInfo(m, frame, view) {
    var info = $('frameInfo');
    clear(info);
    info.appendChild(el('span', null, '帧 ' + (state.frameIdx + 1) + '/' + m.frames.length + '（step ' + frame.stepId + '）'));
    info.appendChild(el('span', null, '事件 ' + frame.events.length + ' 条'));
    info.appendChild(el('span', null, frame.decision ? '决策 P' + frame.decision.player_id + ' · ' + reqCn(frame.decision.request_kind) : '无决策记录'));
    info.appendChild(el('span', null, frame.snapshot ? '快照 hash ' + shortHash(frame.snapshot.state_hash) : '无快照'));
    var isEnd = state.frameIdx === m.frames.length - 1;
    if (isEnd) info.appendChild(el('span', null, '〔终局帧〕'));
  }

  function reqCn(kind) { return REQUEST_CN[kind] || (kind != null ? String(kind) : '未知'); }

  function renderBanner(frame, view) {
    var b = $('requestBanner');
    b.classList.remove('none');
    clear(b);
    var req = view && view.request ? view.request : null;
    var privLocked = state.perspective === 'PRIVILEGED' && !state.privAuthorized;
    if (req && !privLocked) {
      b.appendChild(el('span', null, '当前请求：'));
      b.appendChild(el('span', 'kind', 'P' + (req.player != null ? req.player : '?') + ' · ' + reqCn(req.kind)));
      if (req.options && Object.keys(req.options).length) {
        b.appendChild(el('span', 'mono', ' options=' + jsonText(req.options)));
      }
    } else if (frame.decision) {
      b.appendChild(el('span', null, '当前请求：'));
      b.appendChild(el('span', 'kind', 'P' + frame.decision.player_id + ' · ' + reqCn(frame.decision.request_kind)));
      b.appendChild(el('span', 'mono', '（来自 decision 记录）'));
    } else {
      b.classList.add('none');
      b.appendChild(el('span', null, '当前请求：未知（未记录）'));
    }
  }

  /* ---------- 场面（§3.1） ---------- */
  function renderArena(view) {
    var privLocked = state.perspective === 'PRIVILEGED' && !state.privAuthorized;
    $('privGate').classList.toggle('hidden', !(state.perspective === 'PRIVILEGED' && !state.privAuthorized));
    var bfRow = $('bfRow'), p0 = $('playerBox0'), p1 = $('playerBox1');
    clear(bfRow); clear(p0); clear(p1);
    if (privLocked) {
      bfRow.appendChild(el('div', 'zone', 'Privileged 视角未解锁：确认授权前不渲染任何数据。'));
      return;
    }
    if (!view) {
      bfRow.appendChild(el('div', 'zone', '本帧无快照记录，场面未知（数据缺失一律显示「未知」，不编造）。'));
      renderPlayerPanel(p0, null, 0);
      renderPlayerPanel(p1, null, 1);
      return;
    }
    if (state.perspective === 'PRIVILEGED') {
      var priv = el('div', 'zone');
      priv.appendChild(el('h4', null, 'Privileged 数据'));
      if (view.privilegedStateRef == null) {
        priv.appendChild(el('div', null, '无特权数据（snapshot.privileged_state_ref = null）。下方场面按公开观察呈现。'));
      } else {
        var pre = el('pre', 'raw', jsonText(view.privilegedStateRef));
        priv.appendChild(el('div', null, 'privileged_state_ref：'));
        priv.appendChild(pre);
        priv.appendChild(el('div', null, '下方场面按公开观察呈现。'));
      }
      bfRow.appendChild(priv);
    }
    // 战场区
    if (view.board == null) {
      bfRow.appendChild(el('div', 'zone', '战场信息：未知'));
    } else {
      view.board.forEach(function (bf) { bfRow.appendChild(renderBattlefield(bf, view)); });
    }
    // 结算链（引擎公开观察字段；仅非空时展示，§3.1 可响应窗口的落链情况）
    if (Array.isArray(view.chain) && view.chain.length) {
      var chw = el('div', 'zone');
      chw.appendChild(el('h4', null, '结算链（' + view.chain.length + ' 项）'));
      var chl = el('div', 'mono');
      chl.textContent = view.chain.map(function (ci) {
        if (!ci || typeof ci !== 'object') return '未知';
        var label = ci.def_id != null ? String(ci.def_id) : (ci.kind != null ? String(ci.kind) : '未知');
        if (ci.controller != null) label += '（P' + ci.controller + '）';
        if (ci.status != null) label += '[' + ci.status + ']';
        return label;
      }).join(' → ');
      chw.appendChild(chl);
      bfRow.appendChild(chw);
    }
    renderPlayerPanel(p0, view, 0);
    renderPlayerPanel(p1, view, 1);
  }

  function renderBattlefield(bf, view) {
    var z = el('div', 'zone');
    var h = el('h4');
    h.appendChild(unk(bf == null ? null : (bf.battlefield_def != null ? '战场 ' + bf.battlefield_def : null)));
    if (bf) {
      h.appendChild(unk(bf.battlefield_uid, function (u) { return '[uid:' + u + ']'; }));
      var flags = el('span');
      if (bf.controller != null) flags.appendChild(el('span', 'zflag ctrl', '控制者 P' + bf.controller));
      else flags.appendChild(el('span', 'zflag', '无控制者'));
      if (bf.contested) flags.appendChild(el('span', 'zflag', '争夺中'));
      if (bf.showdown_active) flags.appendChild(el('span', 'zflag', '对决中'));
      if (bf.combat_active) flags.appendChild(el('span', 'zflag', '战斗中'));
      if (view.showdownBf != null && bf.battlefield_uid === view.showdownBf) flags.appendChild(el('span', 'zflag', '对决目标'));
      h.appendChild(flags);
    }
    z.appendChild(h);
    if (!bf) { z.appendChild(unk(null)); return z; }
    // 待命位：内容打码，只显示卡背数量
    var slot = bf.hidden_slot;
    if (Array.isArray(slot) && slot.length) {
      var hd = el('div', 'cards');
      for (var i = 0; i < slot.length; i++) hd.appendChild(el('div', 'card-back', '待命·背面'));
      var hw = el('div');
      hw.appendChild(el('h3', null, '待命位（内容打码 × ' + slot.length + '）'));
      hw.appendChild(hd);
      z.appendChild(hw);
    } else if (Array.isArray(slot)) {
      z.appendChild(el('h3', null, '待命位：空'));
    } else {
      var hw2 = el('h3'); hw2.appendChild(el('span', null, '待命位：')); hw2.appendChild(unk(null)); z.appendChild(hw2);
    }
    // 单位列表
    var occ = bf.occupants;
    if (Array.isArray(occ)) {
      z.appendChild(el('h3', null, '在场单位（' + occ.length + '）'));
      var cards = el('div', 'cards');
      occ.forEach(function (u) { cards.appendChild(renderUnitCard(u)); });
      if (!occ.length) cards.appendChild(el('span', 'unknown', '（空）'));
      z.appendChild(cards);
    } else {
      var hh = el('h3'); hh.appendChild(el('span', null, '在场单位：')); hh.appendChild(unk(null)); z.appendChild(hh);
    }
    return z;
  }

  function renderUnitCard(u) {
    var c = el('div', 'card' + (u && u.exhausted ? ' exhausted' : ''));
    if (!u || typeof u !== 'object') { c.appendChild(unk(null)); return c; }
    c.appendChild(el('div', 'cname', u.name != null ? u.name : '未知'));
    c.appendChild(el('div', 'cuid', 'uid:' + (u.uid != null ? u.uid : '?') +
      ' 控P' + (u.controller != null ? u.controller : '?')));
    var stat = '';
    if (u.might != null) {
      stat = '战力 ' + u.might + (u.might_temp ? (u.might_temp > 0 ? '+' + u.might_temp : u.might_temp) : '') + ' / 伤 ' + (u.damage != null ? u.damage : '?');
    } else if (u.types && u.types.indexOf('rune') >= 0) {
      stat = '符文';
    } else if (u.damage != null) {
      stat = '伤 ' + u.damage;
    }
    if (stat) c.appendChild(el('div', 'cstat', stat));
    var flags = [];
    if (u.exhausted) flags.push('休眠');
    if (u.stunned) flags.push('眩晕');
    if (u.buffs) flags.push('增益×' + u.buffs);
    if (Array.isArray(u.attachments) && u.attachments.length) flags.push('贴附×' + u.attachments.length);
    if (Array.isArray(u.keywords) && u.keywords.length) flags.push(u.keywords.join('/'));
    if (flags.length) c.appendChild(el('div', 'cflags', flags.join(' · ')));
    return c;
  }

  function renderPlayerPanel(box, view, seatIdx) {
    box.className = 'playerPanel' + (perspSeat() === seatIdx ? ' me' : '');
    var seat = view && view.seats ? view.seats[seatIdx] : null;
    var head = el('div', 'phead');
    head.appendChild(el('span', 'pname', '玩家 P' + seatIdx + (perspSeat() === seatIdx ? '（本方视角）' : '')));
    head.appendChild(el('span', null, '分数 '));
    head.appendChild(seat && seat.score != null ? el('span', 'score', String(seat.score)) : el('span', 'unknown', '未知'));
    if (view && view.priority === seatIdx) head.appendChild(el('span', 'tag', '优先权'));
    if (view && view.turn && view.turn.turn_player === seatIdx) head.appendChild(el('span', 'tag green', '回合玩家'));
    box.appendChild(head);

    // 回合信息只在 P0 面板显示一次
    if (seatIdx === 0) {
      var tinfo = el('div', 'stat-grid');
      if (view && view.turn) {
        tinfo.appendChild(statSpan('回合', view.turn.turn_number != null ? String(view.turn.turn_number) : null));
        tinfo.appendChild(statSpan('阶段', view.turn.phase != null ? (PHASE_CN[view.turn.phase] || view.turn.phase) : null));
        if (view.turn.sub_step) tinfo.appendChild(statSpan('子步', view.turn.sub_step));
      } else {
        tinfo.appendChild(statSpan('回合', null));
        tinfo.appendChild(statSpan('阶段', null));
      }
      if (view && view.turnState) {
        tinfo.appendChild(statSpan('模式', view.turnState.mode != null ? view.turnState.mode : null));
        tinfo.appendChild(statSpan('链条', view.turnState.link != null ? view.turnState.link : null));
      } else {
        tinfo.appendChild(statSpan('四态', null));
      }
      if (view && view.ended === true) tinfo.appendChild(statSpan('已结束', '胜方 P' + (view.winner != null ? view.winner : '?')));
      box.appendChild(tinfo);
    }

    var grid = el('div', 'stat-grid');
    grid.appendChild(statSpan('手牌', seat ? seat.handCount : null));
    grid.appendChild(statSpan('主牌堆', seat ? seat.mainDeckCount : null));
    grid.appendChild(statSpan('符文牌堆', seat ? seat.runeDeckCount : null));
    grid.appendChild(statSpan('废牌堆', seat && Array.isArray(seat.trash) ? String(seat.trash.length) : null));
    grid.appendChild(statSpan('放逐', seat && Array.isArray(seat.banish) ? String(seat.banish.length) : null));
    grid.appendChild(statSpan('符文能量', seat ? seat.runeEnergy : null));
    grid.appendChild(statPower(seat ? seat.runePower : null));
    box.appendChild(grid);

    // 手牌：仅本方视角（P0/P1 的 self）有内容；其余一律卡背打码
    if (seat && seat.handExposed) {
      var hh = el('div');
      hh.appendChild(el('h3', null, '手牌（本方可见 ' + seat.hand.length + ' 张）'));
      var cards = el('div', 'cards');
      seat.hand.forEach(function (crd) { cards.appendChild(renderHandCard(crd)); });
      if (!seat.hand.length) cards.appendChild(el('span', 'unknown', '（空）'));
      hh.appendChild(cards);
      box.appendChild(hh);
    } else if (seat && seat.handCount != null) {
      var hb = el('div');
      hb.appendChild(el('h3', null, '手牌（对对方打码 × ' + seat.handCount + '）'));
      var backs = el('div', 'cards');
      var n = Math.min(seat.handCount, 12);
      for (var i = 0; i < n; i++) backs.appendChild(el('div', 'card-back', '手牌'));
      if (seat.handCount > n) backs.appendChild(el('span', 'unknown', '…+' + (seat.handCount - n)));
      hb.appendChild(backs);
      box.appendChild(hb);
    } else {
      var hu = el('h3'); hu.appendChild(el('span', null, '手牌：')); hu.appendChild(unk(null)); box.appendChild(hu);
    }

    // 基地（符文/装备等永久物）
    var base = view && view.bases && view.bases[seatIdx] != null ? view.bases[seatIdx] : null;
    var bw = el('div');
    if (base == null) {
      var bh = el('h3'); bh.appendChild(el('span', null, '基地：')); bh.appendChild(unk(null)); bw.appendChild(bh);
    } else {
      bw.appendChild(el('h3', null, '基地永久物（' + base.length + '）'));
      var bc = el('div', 'cards');
      base.forEach(function (u) { bc.appendChild(renderUnitCard(u)); });
      if (!base.length) bc.appendChild(el('span', 'unknown', '（空）'));
      bw.appendChild(bc);
    }
    box.appendChild(bw);

    // 本方待命牌内容（self_private；其余视角不渲染内容）
    if (seat && seat.hidden) {
      box.appendChild(renderMiniList('待命牌（本方可见）', seat.hidden));
    } else if (seat && seat.handExposed) {
      var hdz = el('h3'); hdz.appendChild(el('span', null, '待命牌（本方可见）：')); hdz.appendChild(unk(null)); box.appendChild(hdz);
    }

    // 公开废牌/放逐列表（公开信息）
    box.appendChild(renderMiniList('废牌堆（公开）', seat ? seat.trash : null));
    box.appendChild(renderMiniList('放逐区（公开）', seat ? seat.banish : null));

    // 英雄/传奇区
    box.appendChild(renderMiniList('英雄区', seat ? seat.heroZone : null));
    box.appendChild(renderMiniList('传奇区', seat ? seat.legendZone : null));
  }

  function perspSeat() {
    if (state.perspective === 'P0') return 0;
    if (state.perspective === 'P1') return 1;
    return -1;
  }

  function statSpan(label, value) {
    var s = el('span');
    s.appendChild(el('span', null, label + ' '));
    if (value == null) s.appendChild(el('b', null, '')).appendChild(unk(null));
    else {
      var b = el('b', null, String(value));
      s.appendChild(b);
    }
    return s;
  }
  function statPower(power) {
    var s = el('span');
    s.appendChild(el('span', null, '符文力 '));
    if (power == null) { s.appendChild(unk(null)); return s; }
    var keys = Object.keys(power);
    var text = keys.length ? keys.map(function (k) { return k + '×' + power[k]; }).join(' ') : '0';
    s.appendChild(el('b', null, text));
    return s;
  }

  function renderHandCard(crd) {
    var c = el('div', 'card');
    if (!crd || typeof crd !== 'object') { c.appendChild(unk(null)); return c; }
    c.appendChild(el('div', 'cname', crd.name != null ? crd.name : '未知'));
    c.appendChild(el('div', 'cuid', 'uid:' + (crd.uid != null ? crd.uid : '?')));
    var bits = [];
    if (crd.cost_energy != null) bits.push('费 ' + crd.cost_energy);
    if (Array.isArray(crd.cost_power) && crd.cost_power.length) bits.push('力 ' + crd.cost_power.join(''));
    if (crd.might != null) bits.push('战力 ' + crd.might);
    if (Array.isArray(crd.types) && crd.types.length) bits.push(crd.types.join('/'));
    if (Array.isArray(crd.keywords) && crd.keywords.length) bits.push(crd.keywords.join('/'));
    if (bits.length) c.appendChild(el('div', 'cstat', bits.join(' · ')));
    return c;
  }

  function renderMiniList(title, list) {
    var w = el('div');
    var h = el('h3');
    h.appendChild(el('span', null, title + '：'));
    if (!Array.isArray(list)) { h.appendChild(unk(null)); w.appendChild(h); return w; }
    h.appendChild(el('span', null, list.length + ' 项'));
    w.appendChild(h);
    if (list.length) {
      var names = list.slice(0, 10).map(function (x) {
        return x && x.name != null ? x.name : '未知';
      }).join('、');
      if (list.length > 10) names += ' …';
      w.appendChild(el('div', 'mono', names));
    }
    return w;
  }

  /* ---------- 事件列表（§3.2 帧内展开） ---------- */
  function renderEvents(frame) {
    var box = $('eventList');
    clear(box);
    if (!frame.events.length) { box.appendChild(el('span', 'unknown', '本帧无事件记录')); return; }
    frame.events.forEach(function (ev) {
      var row = el('div', 'eventRow');
      row.appendChild(el('span', 'seq', '#' + (ev.event_seq != null ? ev.event_seq : '?')));
      var sum = TC.eventSummary(ev);
      row.appendChild(el('span', 'etype' + (sum.known ? '' : ' unknown'), ev.event_type + '·' + sum.typeCn));
      if (sum.payloadText) row.appendChild(el('div', 'payload', sum.payloadText));
      if (Array.isArray(ev.rule_ids) && ev.rule_ids.length) {
        row.appendChild(el('div', 'rules', 'rules: ' + ev.rule_ids.join(', ')));
      }
      if (Array.isArray(ev.card_ids) && ev.card_ids.length) {
        row.appendChild(el('div', 'cards_ref', 'cards: ' + ev.card_ids.join(', ')));
      }
      box.appendChild(row);
    });
  }

  /* ---------- 决策面板（§3.3） ---------- */
  function renderDecision(m, frame) {
    var box = $('decisionPanel');
    clear(box);
    var dec = frame.decision;
    if (!dec) { box.appendChild(el('span', 'unknown', '本帧无决策记录（step ' + frame.stepId + '）')); return; }
    box.appendChild(el('div', null, '请求：P' + dec.player_id + ' · ' + reqCn(dec.request_kind) + '（' + dec.request_kind + '）'));

    // 策略数据：仅在实际记录存在时展示，不虚构
    if (dec.policy && typeof dec.policy === 'object') {
      var pol = el('div');
      pol.appendChild(el('h3', null, '策略输出'));
      var pg = el('div', 'stat-grid');
      pg.appendChild(statSpan('policy_version', dec.policy.policy_version));
      pg.appendChild(statSpan('checkpoint', dec.policy.checkpoint_id));
      pg.appendChild(statSpan('action_prob', dec.policy.action_prob));
      pg.appendChild(statSpan('value', dec.policy.value_estimate));
      pol.appendChild(pg);
      if (Array.isArray(dec.policy.topk) && dec.policy.topk.length) {
        pol.appendChild(el('h3', null, 'top-k'));
        dec.policy.topk.forEach(function (tk) {
          var row = el('div', 'mono');
          var aid = Array.isArray(tk) ? tk[0] : null;
          var prob = Array.isArray(tk) ? tk[1] : null;
          var d = TC.describeAction(typeof aid === 'string' ? aid : null);
          row.textContent = (prob != null ? (Math.round(prob * 1000) / 10) + '%' : '?') + '  ' + d.brief;
          pol.appendChild(row);
        });
      }
      box.appendChild(pol);
    } else {
      var np = el('div'); np.appendChild(el('span', null, '策略输出：')); np.appendChild(el('span', 'unknown', '未记录'));
      box.appendChild(np);
    }

    // 本帧关联规则
    var ruleSet = {};
    frame.events.forEach(function (ev) {
      (ev.rule_ids || []).forEach(function (r) { ruleSet[r] = true; });
    });
    var rules = Object.keys(ruleSet);
    var rn = el('div');
    rn.appendChild(el('span', null, '本帧规则：'));
    rn.appendChild(rules.length ? el('span', 'mono', rules.join(', ')) : el('span', 'unknown', '无'));
    box.appendChild(rn);

    // 合法动作
    var legal = Array.isArray(dec.legal_action_ids) ? dec.legal_action_ids : [];
    box.appendChild(el('h3', null, '合法动作（' + legal.length + '）'));
    legal.forEach(function (aid) {
      var chosen = aid === dec.chosen_action_id;
      var row = el('div', 'actionRow' + (chosen ? ' chosen' : ''));
      var d = TC.describeAction(aid);
      row.appendChild(el('div', null, (chosen ? '✔ ' : '') + d.brief + (chosen ? '（已选）' : '')));
      var det = el('details');
      det.appendChild(el('summary', null, '原始 Action JSON'));
      det.appendChild(el('pre', 'raw', aid));
      row.appendChild(det);
      box.appendChild(row);
    });
    if (!legal.length) {
      var nl = el('div'); nl.appendChild(el('span', null, '合法动作：')); nl.appendChild(el('span', 'unknown', '未知（未记录）'));
      box.appendChild(nl);
    }
    if (dec.chosen_action_id != null && legal.indexOf(dec.chosen_action_id) < 0) {
      box.appendChild(el('div', 'banner-error', '注意：已选动作不在合法集合中（该校验项应在加载阶段拦截）'));
    }
  }

  /* ---------- 动作前后 diff（§3.2） ---------- */
  function renderDiff(m, view) {
    var box = $('diffPanel');
    clear(box);
    var frames = m.frames;
    var cur = frames[state.frameIdx];
    var prevFrame = state.frameIdx > 0 ? frames[state.frameIdx - 1] : null;
    if (!cur.snapshot || !prevFrame || !prevFrame.snapshot) {
      var d0 = el('div'); d0.appendChild(el('span', null, 'diff：'));
      d0.appendChild(el('span', 'unknown', state.frameIdx === 0 ? '首帧，无前置快照' : '相邻帧快照缺失（未知）'));
      box.appendChild(d0);
      return;
    }
    if (state.perspective === 'PRIVILEGED' && !state.privAuthorized) {
      box.appendChild(el('span', 'unknown', 'Privileged 未解锁'));
      return;
    }
    var persp = state.perspective === 'PRIVILEGED' ? 'OBSERVER' : state.perspective;
    var before = TC.deriveView(prevFrame.snapshot, persp);
    var after = TC.deriveView(cur.snapshot, persp);
    var diffs = TC.diffViews(before, after);
    box.appendChild(el('div', 'mono', '快照 step ' + prevFrame.stepId + ' → ' + cur.stepId + '（diff ' + diffs.length + ' 项）'));
    if (!diffs.length) { box.appendChild(el('span', 'unknown', '公开状态无变化')); return; }
    diffs.slice(0, 80).forEach(function (d) {
      var row = el('div', 'diffRow diff-' + d.kind);
      var mark = d.kind === 'new' ? '＋' : d.kind === 'removed' ? '－' : '＊';
      row.appendChild(el('span', 'dpath', mark + ' ' + d.path + '：'));
      var valText;
      if (d.kind === 'new') valText = '新增 ' + leafText(d.after);
      else if (d.kind === 'removed') valText = '移除 ' + leafText(d.before);
      else valText = leafText(d.before) + ' → ' + leafText(d.after);
      row.appendChild(el('span', 'dval', valText));
      box.appendChild(row);
    });
    if (diffs.length > 80) box.appendChild(el('div', 'mono', '…另有 ' + (diffs.length - 80) + ' 项未显示'));
  }
  function leafText(v) {
    if (v === undefined) return '（无）';
    if (v === null) return 'null';
    if (typeof v === 'object') return TC.abbrev(v, 80);
    return String(v);
  }

  /* ---------- 终局面板（VM-1 #4） ---------- */
  function renderFooter(m) {
    var box = $('footerPanel');
    clear(box);
    var f = m.parsed.footer ? m.parsed.footer.rec : null;
    if (!f) { box.appendChild(el('span', 'unknown', '无 footer 记录')); return; }
    var res = f.result || {};
    var len = f.length || {};
    var tc = f.trace_completeness || null;
    var parts = el('div');
    parts.appendChild(el('b', null, '终局：'));
    parts.appendChild(el('span', null, res.winner != null ? ' 胜方 P' + res.winner : ' 胜方 未知'));
    parts.appendChild(el('span', null, ' · 终止 ' + (res.termination_reason != null ? res.termination_reason : '未知')));
    if (res.modal_winner === true) parts.appendChild(el('span', 'tag', '按模态判胜'));
    var rw = f.reward_by_player;
    if (rw && typeof rw === 'object') parts.appendChild(el('span', 'mono', ' 奖励 ' + jsonText(rw)));
    parts.appendChild(el('span', null, ' · 步 ' + (len.decision_steps != null ? len.decision_steps : '?') +
      ' · 回合 ' + (len.turns != null ? len.turns : '?') + ' · 事件 ' + (len.events != null ? len.events : '?') +
      ' · 非法动作 ' + (f.invalid_action_count != null ? f.invalid_action_count : '?')));
    box.appendChild(parts);
    var fin = el('div', 'final');
    fin.appendChild(el('span', null, 'final_state_hash='));
    fin.appendChild(el('span', 'mono', f.final_state_hash != null ? f.final_state_hash : '未知'));
    box.appendChild(fin);
    var comp = el('div');
    comp.appendChild(el('span', null, '完整性：'));
    if (tc) {
      comp.appendChild(el('span', tc.ok === true ? 'tag green' : 'tag red',
        'expected=' + tc.expected_events + ' written=' + tc.written_events + ' ok=' + tc.ok));
    } else comp.appendChild(el('span', 'unknown', '未知'));
    comp.appendChild(el('span', m.validation.ok ? 'tag green' : 'tag red', m.validation.ok ? '回放器校验 PASS' : '回放器校验 FAIL'));
    box.appendChild(comp);
  }

  /* ---------- 播放控制 ---------- */
  function stepFrame(delta) {
    var m = current();
    if (!m) return;
    var next = state.frameIdx + delta;
    if (next < 0 || next >= m.frames.length) { stopPlay(); return; }
    state.frameIdx = next;
    renderFrame();
  }
  function playInterval() {
    var speed = parseFloat($('speedSel').value) || 1;
    return 900 / speed;
  }
  function startPlay() {
    var m = current();
    if (!m || state.playing) return;
    state.playing = true;
    $('btnPlay').textContent = '⏸ 暂停';
    state.timer = setInterval(function () {
      if (state.frameIdx >= m.frames.length - 1) { stopPlay(); return; }
      stepFrame(1);
    }, playInterval());
  }
  function stopPlay() {
    if (state.timer) { clearInterval(state.timer); state.timer = null; }
    state.playing = false;
    var b = $('btnPlay'); if (b) b.textContent = '▶ 播放';
  }

  /* ---------- 事件绑定 ---------- */
  function bind() {
    $('fileInput').addEventListener('change', function (e) { loadFiles(e.target.files); e.target.value = ''; });
    document.addEventListener('dragover', function (e) { e.preventDefault(); document.body.classList.add('dragging'); });
    document.addEventListener('dragleave', function (e) { if (e.target === document.body) document.body.classList.remove('dragging'); });
    document.addEventListener('drop', function (e) {
      e.preventDefault();
      document.body.classList.remove('dragging');
      if (e.dataTransfer && e.dataTransfer.files) loadFiles(e.dataTransfer.files);
    });
    $('btnPrev').addEventListener('click', function () { stopPlay(); stepFrame(-1); });
    $('btnNext').addEventListener('click', function () { stopPlay(); stepFrame(1); });
    $('btnPlay').addEventListener('click', function () { if (state.playing) stopPlay(); else startPlay(); });
    $('speedSel').addEventListener('change', function () {
      if (state.playing) { stopPlay(); startPlay(); }
    });
    $('timelineSlider').addEventListener('input', function (e) {
      stopPlay();
      state.frameIdx = parseInt(e.target.value, 10) || 0;
      renderFrame();
    });
    $('btnAnchor').addEventListener('click', function () {
      var v = $('anchorSelect').value;
      if (v === '') return;
      stopPlay();
      state.frameIdx = parseInt(v, 10) || 0;
      renderFrame();
    });
    Array.prototype.forEach.call(document.querySelectorAll('.perspBtn'), function (btn) {
      btn.addEventListener('click', function () {
        state.perspective = btn.getAttribute('data-persp');
        Array.prototype.forEach.call(document.querySelectorAll('.perspBtn'), function (b) {
          b.classList.toggle('active', b === btn);
        });
        renderFrame();
      });
    });
    $('btnPrivAuth').addEventListener('click', function () {
      state.privAuthorized = true;
      renderFrame();
    });
    document.addEventListener('keydown', function (e) {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA')) {
        if (e.target === $('timelineSlider') && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
          // slider 自带步进即可，不重复处理
          return;
        }
        if (e.target !== $('timelineSlider')) return;
      }
      if (e.key === 'ArrowLeft') { e.preventDefault(); stopPlay(); stepFrame(-1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); stopPlay(); stepFrame(1); }
      else if (e.key === ' ') {
        if ($('replaySection').classList.contains('hidden')) return;
        e.preventDefault();
        if (state.playing) stopPlay(); else startPlay();
      }
    });
  }

  bind();
})();
