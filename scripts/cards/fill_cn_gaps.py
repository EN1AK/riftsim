# 对照 EN 补齐 CN 缺段候选生成（2026-09-30；应对 cards_cn 装备类 effect 只抓主段的既有数据缺陷）
# 输出 .tmp/cn_gaps_candidates.md 对照清单 + .tmp/cn_gaps_apply.sql（人工 review 后执行）
# 不直接写库！机器对照只作参考，中文行需卡面/官方 CN 文本逐卡校对。
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "cards_bilingual.db"

# EN 关键词占位 -> CN 关键词占位（中英官方术语一一对应）
KW_MAP = [
    (r"\[Equip\]\s*(:[^\s:]+:)*", "{{装配}}"),
    (r"\[Weaponmaster\]", "{{百炼}}"),
    (r"\[Hunt\]", "{{狩猎}}"),
    (r"\[Deathknell\]", "{{绝念}}"),
    (r"\[Level (\d+)\]\[>\]", r"{{等级\1}}"),
    (r"\[Assault (\d+)\]", r"{{强攻\1}}"),
    (r"\[Deflect (\d+)\]", r"{{法盾\1}}"),
    (r"\[Shield (\d+)\]", r"{{坚守\1}}"),
    (r"\[Ganking\]", "{{游走}}"),
    (r"\[Quick-Draw\]", "{{灵便}}"),
    (r"\[Temporary\]", "{{瞬息}}"),
    (r"\[Accelerate\]", "{{急速}}"),
    (r"\[Reaction\]", "{{反应}}"),
    (r"\[Action\]", "{{迅捷}}"),
    (r"\[Ambush\]", "{{伏击}}"),
    (r"\[Hidden\]", "{{待命}}"),
    (r"\[Vision\]", "{{预知}}"),
    (r"\[Tank\]", "{{壁垒}}"),
    (r"\[Unique\]", "{{出身名门}}"),
    (r"\[Backline\]", "{{后排}}"),
    (r"\[Flow\]\s*(:[^\s:]+:)+", "{{流转}}"),
    (r"\[Burn (\d+)\]", r"{{燃烧\1}}"),
    (r"\[Empower\]\s*(:[^\s:]+:)*", "{{强化}}"),
    (r"\[Empowered\]", "{{强化}}"),
    (r"\[Repeat (\d+)\]\[>\]", r"{{回响\1}}"),
]
DOMAIN_ICONS = {
    ":rb_rune_fury:": "{{红色}}", ":rb_rune_calm:": "{{绿色}}",
    ":rb_rune_mind:": "{{蓝色}}", ":rb_rune_body:": "{{橙色}}",
    ":rb_rune_chaos:": "{{紫色}}", ":rb_rune_order:": "{{黄色}}",
    ":rb_rune_rainbow:": "{{A}}",
    ":rb_rainbow:": "{{A}}",
    ":rb_exhaust:": "{{横置}}", ":rb_might:": "{{S}}",
}
ENERGY_RE = re.compile(r":rb_energy_(\d+):")

PLAYS_PATTERNS = [
    # 句式 → CN 模板生成（[...] 表示需校对/保留原文占位）
    (re.compile(r"^At the end of your turn, if I didn'?t conquer this turn, unattach this and deal (\d+) to me\."),
     lambda m: f"在你的回合结束时，如果我未在本回合内征服，将此牌卸除，并对我造成{m.group(1)}点伤害。"),
    (re.compile(r"^When I attack or defend, deal (\d+) to an enemy unit here\."),
     lambda m: f"当我进攻或防守时，对战场上的一名敌方单位造成{m.group(1)}点伤害。"),
    (re.compile(r"^When I attack or defend, deal (\d+) to all enemy units here\."),
     lambda m: f"当我进攻或防守时，对此处所有敌方单位造成{m.group(1)}点伤害。"),
    (re.compile(r"^When I (?:conquer|hold), (?:play|channel) (?:a )?(\d+|an?)? ?(\w+)? ?(?:gear )?(?:unit )?tokens? (?:runes? )?exhausted\."),
     lambda m: f"当我{'征服' if 'conquer' in m.group(0) else '据守'}时，打出{'两' if m.group(1)=='two' else m.group(1)}个休眠的“{m.group(2).title()}”装备指示物。" if m.group(1) else "[机器模板未覆盖]"),
    (re.compile(r"^When I conquer, score (\d+) point\."),
     lambda m: f"当我征服一处战场时，你获得{m.group(1)}分。"),
    (re.compile(r"^When I hold, score (\d+) point\."),
     lambda m: f"当我据守一处战场时，你获得{m.group(1)}分。"),
    (re.compile(r"^When I conquer, buff me\."),
     lambda m: "当我征服一处战场时，给予我增益。"),
    (re.compile(r"^When I conquer, channel (\d+) runes? exhausted\."),
     lambda m: f"当我征服一处战场时，召出{m.group(1)}枚休眠的符文。"),
    (re.compile(r"^When I conquer, discard (\d+), then draw (\d+)\."),
     lambda m: f"当我征服一处战场时，弃置{m.group(1)}张手牌，然后抽{m.group(2)}张。"),
    (re.compile(r"^When I move, play a (\d+) :rb_might: (\w+) unit token (?:here|to this battlefield)\."),
     lambda m: f"当我移动时，打出一名{m.group(1)}{{S}}的“{m.group(2).title()}”单位指示物。"),
    (re.compile(r"^When (?:this|it|the gear|this card) was attached to me this turn, I have an additional \+(\d+) :rb_might:\."),
     lambda m: f"在本回合内贴附于此单位期间，我额外获得+{m.group(1)}{{S}}。"),
    (re.compile(r"^Your units here have \[Ganking\]\."),
     lambda m: "你控制于此处的所有单位均具有{{游走}}。"),
    (re.compile(r"^I am a (\w+)\."),
     lambda m: f"我是一张{m.group(1)}。"),
]


def strip_reminders(offset_lines: list[str]) -> list[str]:
    """剥离 reminder/cost 说明段的常见句式（括号/破折号后），便于判断是否真效果行。"""
    out = []
    for ln in offset_lines:
        s = re.sub(r"\([^)]*\)", "", ln).strip()
        if s:
            out.append(ln)
    return out


def to_cn(line: str) -> str:
    """机翻单条 EN 效果行为 CN 占位行——模板未覆盖时预留 [TRANSLATE] 标记。"""
    t = line
    for pat, fn in PLAYS_PATTERNS:
        m = pat.match(t)
        if m:
            r = fn(m)
            if not r.startswith("[机器模板未覆盖]"):
                return r
            break
    # domain/图标替换 + 关键词替换
    for icon, cn in DOMAIN_ICONS.items():
        t = t.replace(icon, cn)
    t = ENERGY_RE.sub(lambda m: f"{{{{{m.group(1)}}}}}", t)
    for pat, repl in KW_MAP:
        t = re.sub(pat, repl, t)
    return f"[需校对] {t}"


def main() -> None:
    con = sqlite3.connect(str(DB))
    rows = con.execute(
        "SELECT card_key, name_cn, text_en, text_cn FROM cards WHERE text_en IS NOT NULL"
    ).fetchall()
    con.close()

    md = ["# CN 缺段补齐候选（对照 EN effect 段）\n",
          "> 机器参考 = 模板机翻+术语映射；逐卡校对英文原文后手工改中文。**一切都是候选**，须经人工确认再入库。\n"]
    sql: list[str] = ["-- 执行前需人工核对上方 md；取消 'BEGIN;' 注释后事务执行", "-- BEGIN;"]
    n_done = 0
    for k, nm, t_en, t_cn in rows:
        t_en = t_en or ""
        t_cn = t_cn or ""
        en_lines = [ln.strip() for ln in t_en.splitlines() if ln.strip()]
        cn_lines = [ln.strip() for ln in t_cn.splitlines() if ln.strip()]
        if len(en_lines) <= len(cn_lines):
            continue
        gaps = en_lines[len(cn_lines):]
        md.append(f"\n## {k} {nm}（EN {len(en_lines)}行 / CN {len(cn_lines)}行）")
        md.append(f"- CN 已有：")
        for ln in cn_lines:
            md.append(f"  - `{ln}`")
        proposed_cn = []
        for g in gaps:
            cand = to_cn(g)
            proposed_cn.append(cand)
            md.append(f"- 缺段 EN：`{g}`")
            md.append(f"  - 候选 CN：`{cand}`")
        if proposed_cn:
            # 生成 UPDATE SQL（追加据段）
            new_cn = (t_cn + "\n" + "\n".join(proposed_cn)).strip()
            esc = new_cn.replace("'", "''")
            sql.append(
                f"UPDATE cards SET text_cn = '{esc}' WHERE card_key = '{k}';  -- {k} {nm}"
            )
            n_done += 1
    Path(ROOT / ".tmp").mkdir(exist_ok=True)
    Path(ROOT / ".tmp" / "cn_gaps_candidates.md").write_text("\n".join(md), encoding="utf-8")
    Path(ROOT / ".tmp" / "cn_gaps_apply.sql").write_text("\n".join(sql), encoding="utf-8")
    print(f"cards scanned={len(rows)}; candidates={n_done}")
    print("written .tmp/cn_gaps_candidates.md  and  .tmp/cn_gaps_apply.sql")


if __name__ == "__main__":
    main()
