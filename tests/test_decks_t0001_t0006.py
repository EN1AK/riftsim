# 组卡校验（T-0001..T-0006；R-CR-101..103）
from riftsim.cards import CardDefinition, DeckList, basic_rune, make_skeleton_deck, skeleton_battlefield, skeleton_hero, skeleton_legend, skeleton_spell
from riftsim.decks import validate_deck
from riftsim.enums import CardType, Domain


def test_t0001_valid_deck():
    assert validate_deck(make_skeleton_deck("A", "hero-a")) == []


def test_t0002_four_copies_illegal():
    deck = make_skeleton_deck("A", "hero-a")
    extra = next(c for c in deck.main_deck if c.def_id == "sk:unit:u2:1")
    bad = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                   main_deck=(*deck.main_deck[:1], *([extra] * 4), *deck.main_deck[5:]),
                   rune_deck=deck.rune_deck, battlefields=deck.battlefields, deck_id="bad")
    v = validate_deck(bad)
    assert any("同名" in x and "u2" in x.lower() or "同名卡" in x for x in v)


def test_t0003_domain_mismatch_illegal():
    deck = make_skeleton_deck("A", "hero-a")
    g_card = CardDefinition(def_id="t:g", name="蓝卡", card_types=frozenset({CardType.UNIT}),
                            domains=frozenset({Domain.G}), cost_energy=2, might=2)
    deck_bad = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                        main_deck=(g_card, *deck.main_deck), rune_deck=deck.rune_deck,
                        battlefields=deck.battlefields, deck_id="bad")
    assert any("103.1.b.3" in x for x in validate_deck(deck_bad))
    # 多特性卡：须全部特性属于卡组（[R]+[G] 进 [R] 卡组非法）
    rg = CardDefinition(def_id="t:rg", name="双卡", card_types=frozenset({CardType.UNIT}),
                        domains=frozenset({Domain.R, Domain.G}), cost_energy=2, might=2)
    deck_bad2 = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                         main_deck=(rg, *deck.main_deck), rune_deck=deck.rune_deck,
                         battlefields=deck.battlefields, deck_id="bad")
    assert any("103.1.b.4" in x for x in validate_deck(deck_bad2))
    # 符文特性不符（103.3.a.1）
    g_rune = basic_rune(99, Domain.G)
    deck_bad3 = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                         main_deck=deck.main_deck, rune_deck=(*deck.rune_deck[:11], g_rune),
                         battlefields=deck.battlefields, deck_id="bad")
    assert any("103.3.a.1" in x for x in validate_deck(deck_bad3))


def test_t0004_signature_and_hero_tag():
    deck = make_skeleton_deck("A", "hero-a")
    # 英雄标签不匹配的选定英雄
    other_hero = skeleton_hero("hero-x")
    bad = DeckList(legend=deck.legend, chosen_hero=other_hero,
                   main_deck=(other_hero, *deck.main_deck[1:]), rune_deck=deck.rune_deck,
                   battlefields=deck.battlefields, deck_id="bad")
    assert any("103.2.a.2" in x for x in validate_deck(bad))
    # 专属卡 4 张
    sigs = tuple(
        CardDefinition(def_id=f"t:sig:{i}", name=f"专属{i}", card_types=frozenset({CardType.UNIT}),
                       domains=frozenset({Domain.R}), cost_energy=1, might=1,
                       tags=frozenset({"signature"}), hero_tag="hero-a")
        for i in range(4)
    )
    bad2 = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                    main_deck=(*sigs, *deck.main_deck), rune_deck=deck.rune_deck,
                    battlefields=deck.battlefields, deck_id="bad")
    assert any("103.2.d" in x for x in validate_deck(bad2))


def test_t0005_rune_deck_size():
    deck = make_skeleton_deck("A", "hero-a")
    bad = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                   main_deck=deck.main_deck, rune_deck=deck.rune_deck[:11],
                   battlefields=deck.battlefields, deck_id="bad")
    assert any("103.3.a" in x and "12" in x for x in validate_deck(bad))


def test_t0006_same_battlefield_twice():
    deck = make_skeleton_deck("A", "hero-a")
    b = deck.battlefields[0]
    bad = DeckList(legend=deck.legend, chosen_hero=deck.chosen_hero,
                   main_deck=deck.main_deck, rune_deck=deck.rune_deck,
                   battlefields=(b, b, deck.battlefields[1]), deck_id="bad")
    assert any("103.4.c" in x for x in validate_deck(bad))
