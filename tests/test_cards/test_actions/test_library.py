from typing import Optional

from pyminion.bots import OptimizedBot
from pyminion.expansions.base import copper, duchy, estate, gold, library, smithy
from pyminion.game import Game
from pyminion.players import Human


def test_library_draw_7(human: Human, game: Game, monkeypatch):
    human.hand.add(library)
    human.play(library, game)
    assert len(human.hand) == 7
    assert len(human.playmat) == 1
    assert human.state.actions == 0


def test_library_skip_action(human: Human, game: Game, monkeypatch):
    human.deck.add(smithy)
    human.hand.add(library)
    assert len(human.discard_pile) == 0

    monkeypatch.setattr("builtins.input", lambda _: "yes")

    human.play(library, game)
    assert len(human.hand) == 7
    assert len(human.discard_pile) == 1
    assert human.discard_pile.cards[0].name == "Smithy"


def test_library_keep_action(human: Human, game: Game, monkeypatch):
    human.deck.add(smithy)
    human.hand.add(library)
    assert len(human.discard_pile) == 0

    monkeypatch.setattr("builtins.input", lambda _: "no")

    human.play(library, game)
    assert len(human.hand) == 7
    assert len(human.discard_pile) == 0


def test_library_bot(bot: OptimizedBot, game: Game):
    bot.hand.add(library)
    bot.play(library, game)
    assert len(bot.hand) == 7
    assert len(bot.playmat) == 1
    assert bot.state.actions == 0


def test_library_bot_no_action(bot: OptimizedBot, game: Game):
    bot.hand.add(library)
    bot.deck.add(smithy)
    bot.play(library, game)
    assert len(bot.hand) == 7
    assert len(bot.discard_pile) == 1


def test_library_bot_extra_action(bot: OptimizedBot, game: Game):
    bot.hand.add(library)
    bot.state.actions = 2
    bot.deck.add(smithy)
    bot.play(library, game)
    assert len(bot.hand) == 7
    assert len(bot.discard_pile) == 0