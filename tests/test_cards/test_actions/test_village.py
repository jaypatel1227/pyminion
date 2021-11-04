from pyminion.models.core import Player
from pyminion.game import Game
from pyminion.models.base import Village
from pyminion.expansions.base import village


def test_village(player: Player, game: Game):
    player.hand.add(village)
    assert len(player.hand) == 1
    player.hand.cards[0].play(player, game)
    assert len(player.hand) == 1
    assert len(player.playmat) == 1
    assert type(player.playmat.cards[0]) is Village
    assert player.state.actions == 2
