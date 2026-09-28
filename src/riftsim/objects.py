# GameObject 运行时实例（MECH-GAME-OBJECTS；跨区域迁移新身份由 124 规则处理：
# M1 骨架引擎采用“对象 uid 不变、记录区域迁移事件”的实现，绝念/最后状态等需要
# 身份语义的挂点通过 last_known 快照表达——P1 若遇身份敏感卡再引入重实例化）。
from __future__ import annotations

from dataclasses import dataclass, field

from .enums import Keyword, Zone


@dataclass
class GameObject:
    uid: int
    def_id: str
    owner: int            # 所属者（R-CR-127：对局中不变）
    controller: int       # 控制者（R-CR-188..192）
    zone: Zone
    zone_owner: int | None = None   # 所在区域的归属玩家（base/hand/deck 等）；战场=None
    battlefield: int | None = None  # zone 为 BATTLEFIELD/HIDDEN_SLOT 时的战场索引
    damage: int = 0                 # 累积伤害标记（R-CR-142/417）
    exhausted: bool = False         # 休眠（414）
    stunned: bool = False           # 眩晕（423；回合结束 3d 失去）
    face_down: bool = False         # 牌面朝下（待命 811；牌堆天然朝下不以此字段表示）
    might_temp: int = 0             # 回合内临时战力修正（3d 清零；P1 Layers 接管）
    buffs: int = 0                  # 增益计数标（701..705，每单位≤1）
    keywords_extra: dict[Keyword, str] = field(default_factory=dict)
    # keyword -> duration："turn"(3d 清除) | "perm"(至离场)（R-CR-801.3.a.3/b.2 默认时长）
    attachments: list[int] = field(default_factory=list)  # 本卡下方的贴附卡 uid 序（顶卡=自己）
    attached_to: int | None = None                        # 本卡作为贴附卡挂载的顶部卡 uid
    counters: dict[str, int] = field(default_factory=dict)  # 计数标（741..749）
    entered_turn: int = 0           # 进场回合号（急速/召唤失调备查）
    last_known: dict | None = None  # 离场快照（绝念 808.1.d.2/3 用）

    def snapshot_last_known(self, might: int) -> None:
        """离场前记录最后状态（R-CR-808.1.d.2/.3）。"""
        self.last_known = {
            "uid": self.uid,
            "def_id": self.def_id,
            "zone": self.zone.value,
            "battlefield": self.battlefield,
            "controller": self.controller,
            "might": might,
            "damage": self.damage,
            "exhausted": self.exhausted,
            "keywords_extra": sorted(k.value for k in self.keywords_extra),
            "buffs": self.buffs,
        }
