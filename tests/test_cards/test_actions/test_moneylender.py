from pyminion.bots import Bot
from pyminion.players import Human
from pyminion.game import Game
from pyminion.models.base import Moneylender, Copper
from pyminion.expansions.base import moneylender, copper


def test_moneylender_human_input_yes(human: Human, game: Game, monkeypatch):
    human.hand.add(moneylender)
    human.hand.add(copper)
    assert len(human.hand) == 2
    assert len(game.trash) == 0

    monkeypatch.setattr("builtins.input", lambda _: "y")

    human.hand.cards[0].play(human, game)
    assert len(human.hand) == 0
    assert len(human.playmat) == 1
    assert type(human.playmat.cards[0]) is Moneylender
    assert human.state.actions == 0
    assert human.state.money == 3
    assert len(game.trash) == 1
    assert type(game.trash.cards[0]) is Copper


def test_moneylender_human_input_no(human: Human, game: Game, monkeypatch):
    human.hand.add(moneylender)
    human.hand.add(copper)
    assert len(human.hand) == 2
    assert len(game.trash) == 0

    monkeypatch.setattr("builtins.input", lambda _: "n")

    human.hand.cards[0].play(human, game)
    assert len(human.hand) == 1
    assert len(human.playmat) == 1
    assert type(human.playmat.cards[0]) is Moneylender
    assert human.state.actions == 0
    assert human.state.money == 0
    assert len(game.trash) == 0


def test_moneylender_human_no_coppers(human: Human, game: Game, monkeypatch):
    human.hand.add(moneylender)
    assert len(human.hand) == 1
    assert len(game.trash) == 0
    human.hand.cards[0].play(human, game)
    assert len(human.hand) == 0
    assert len(human.playmat) == 1
    assert type(human.playmat.cards[0]) is Moneylender
    assert human.state.actions == 0
    assert human.state.money == 0
    assert len(game.trash) == 0


def test_moneylender_bot_input_yes(bot: Bot, game: Game):
    bot.hand.add(moneylender)
    bot.hand.add(copper)
    assert len(bot.hand) == 2
    assert len(game.trash) == 0

    bot.hand.cards[0].play(bot, game)
    assert len(bot.hand) == 0
    assert len(bot.playmat) == 1
    assert type(bot.playmat.cards[0]) is Moneylender
    assert bot.state.actions == 0
    assert bot.state.money == 3
    assert len(game.trash) == 1
    assert type(game.trash.cards[0]) is Copper
