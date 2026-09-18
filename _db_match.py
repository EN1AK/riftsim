# -*- coding: utf-8 -*-
import sqlite3, json, re, sys
io = sys.stdout
conn = sqlite3.connect(r"c:\Users\Mortis\Desktop\Workspace\riftsim\cards_bilingual.db")
cur = conn.cursor()
cur.execute("SELECT card_key, name_en, name_cn, sub_title_cn, hero_cn, set_id, errata_cn FROM cards")
rows = cur.fetchall()

def norm(s):
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[\s\-–—,，'’\.\-:·、（）()！!\"“”]", "", s)
    return s

# names we need to find
targets = [
    # EN names
    "Ava Achiever","Baited Hook","Blind Fury","Clockwork Keeper","Convergent Mutation",
    "Dark Child, Starter","Dazzling Aurora","Disintegrate","Dragon's Rage","Dune Drake",
    "Highlander","Karma, Channeler","Kinkou Monk","Nocturne, Horrifying","Pack of Wonders",
    "Portal Rescue","Promising Future","Ravenborn Tome","Salvage","Sigil of the Storm",
    "Sona, Harmonious","Targon's Peak","Teemo, Strategist","The Boss","The Dreaming Tree",
    "The Syren","Tideturner","Unforgiven","Unlicensed Armory","Void Gate","Zhonya's Hourglass",
    "Falling Star","Icathian Rain","Reinforce","Arise!","Blood Rush","Deathgrip","Edge of Night",
    "Janna, Savior","Jax, Unmatched","Kato the Arm","Rek'Sai, Swarm Queen","Rell, Magnetic",
    "Tianna Crownguard","Void Burrower","Void Rush","Yone, Blademaster","Guards!",
    "Relentless Pursuit","Death from Below","Bone Skewer","Leblanc, Deceiver","Mirror Image",
    "Keeper of Masks","Rengar, Trophy Hunter","Draven, Vanquisher","Emperor's Dais",
    "Fizz, Trickster","Diana, Lunari","Stalking Wolf","Astral Heron","Gangplank, Naval",
    "Resonating Strike",
    # CN names
    "斥候标兵 艾娃","海兽钓钩","暴怒冲动","小小守护者","聚合变异","黑暗之女 - 入门","闪耀极光",
    "碎裂之火","猛龙摆尾","沙丘亚龙","高原血统","卡尔玛 - 圣灵之媒","均衡僧侣","魔腾 - 惊魂夜",
    "奇妙行囊","传送门大营救","光明未来","邪鸦魔典","废物利用","雷霆之纹","娑娜 - 清心谐律",
    "巨神峰之巅","提莫，军事家","腕豪","幻梦之树","塞壬号","控潮者","疾风剑豪","来路不明的武器",
    "虚空之门","中娅沙漏","星落","艾卡西亚暴雨","增援","沙兵现身","血性冲刺","断魂一扼",
    "夜之锋刃","迦娜 - 救世之灵","贾克斯 - 万般皆武","巨腕加藤","雷克塞 - 万类女皇",
    "芮尔 - 唯心铁意","缇亚娜·冕卫","虚空遁地兽","虚空猛冲","永恩 - 一剑封尘","沉没神庙",
    "遗忘丰碑","护驾！","冷酷追击","涌泉之恨","透骨尖钉","乐芙兰 - 诡术妖姬","镜花水月",
    "赐面守侍","雷恩加尔 - 异兽猎手","倾颓宫殿","击退","苍蓝雕纹魔像","圣裁之刻","宏伟广场",
    "卡尔萨斯 - 永恒颂葬","厄运小姐 - 海盗","伊泽瑞尔-奥法逸才","黛安娜-皎月化身",
    "兰博 - 热力全开","杰斯 – 推陈出新","德莱文 - 血斧飞旋","暗巷神偷","临终仪式","奥恩的锻炉",
    "帝王神坛","蔚 - 铲除者","咂魂者","自适应机器人","粗鲁的海盗","冥想","痛殴","荣耀召唤",
    "菲兹 - 捣蛋鬼","追猎雪狼","星界灵鹭","普朗克 - 海上霸主","回音击","时间扭曲","忠诚的猎犬",
    "夺魂钩 妲姆",
]

result = {}
for t in targets:
    nt = norm(t)
    hits = []
    for key, ne, nc, sub, hero, set_id, err in rows:
        cands = set()
        for v in (ne, nc, sub, hero):
            if v:
                cands.add(norm(v))
        if nc and sub:
            for sep in ("", "-", "–", " ", " - ", "—"):
                cands.add(norm(nc + sep + sub))
                cands.add(norm(sub + sep + nc))
        if hero and sub:
            cands.add(norm(hero + sub)); cands.add(norm(sub + hero))
        if nt in cands:
            hits.append((key, ne, nc, sub, set_id))
    result[t] = hits

with open(r"c:\Users\Mortis\Desktop\Workspace\riftsim\_db_match_out.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

for t, hits in result.items():
    status = hits if hits else "NOT FOUND"
    io.write("%s => %s\n" % (t, status))
conn.close()
