import logging
import math
from typing import TYPE_CHECKING, List, Tuple

from pyminion.core import AbstractDeck, CardType, Action, Card, ScoreCard, Treasure, Victory
from pyminion.effects import AttackEffect, EffectAction, FuncPlayerCardGameEffect, FuncPlayerGameEffect, PlayerCardGameEffect
from pyminion.exceptions import EmptyPile
from pyminion.player import Player

if TYPE_CHECKING:
    from pyminion.game import Game


logger = logging.getLogger()


class Copper(Treasure):
    def __init__(
        self,
        name: str = "Copper",
        cost: int = 0,
        type: Tuple[CardType, ...] = (CardType.Treasure,),
        money: int = 1,
    ):
        super().__init__(name, cost, type, money)

    def get_pile_starting_count(self, game: "Game") -> int:
        num_players = len(game.players)
        return 60 - (7 * num_players)

    def play(self, player: Player, game: "Game") -> None:
        player.playmat.add(self)
        player.hand.remove(self)
        player.state.money += self.money


class Silver(Treasure):
    def __init__(
        self,
        name: str = "Silver",
        cost: int = 3,
        type: Tuple[CardType, ...] = (CardType.Treasure,),
        money: int = 2,
    ):
        super().__init__(name, cost, type, money)

    def get_pile_starting_count(self, game: "Game") -> int:
        return 40

    def play(self, player: Player, game: "Game") -> None:
        player.playmat.add(self)
        player.hand.remove(self)
        player.state.money += self.money


class Gold(Treasure):
    def __init__(
        self,
        name: str = "Gold",
        cost: int = 6,
        type: Tuple[CardType, ...] = (CardType.Treasure,),
        money: int = 3,
    ):
        super().__init__(name, cost, type, money)

    def get_pile_starting_count(self, game: "Game") -> int:
        return 30

    def play(self, player: Player, game: "Game") -> None:
        player.playmat.add(self)
        player.hand.remove(self)
        player.state.money += self.money


class Estate(Victory):
    def __init__(
        self,
        name: str = "Estate",
        cost: int = 2,
        type: Tuple[CardType, ...] = (CardType.Victory,),
    ):
        super().__init__(name, cost, type)

    def score(self, player: Player) -> int:
        vp = 1
        return vp


class Duchy(Victory):
    def __init__(
        self,
        name: str = "Duchy",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Victory,),
    ):
        super().__init__(name, cost, type)

    def score(self, player: Player) -> int:
        vp = 3
        return vp


class Province(Victory):
    def __init__(
        self,
        name: str = "Province",
        cost: int = 8,
        type: Tuple[CardType, ...] = (CardType.Victory,),
    ):
        super().__init__(name, cost, type)

    def score(self, player: Player) -> int:
        vp = 6
        return vp


class Curse(ScoreCard):
    def __init__(
        self,
        name: str = "Curse",
        cost: int = 0,
        type: Tuple[CardType, ...] = (CardType.Curse,),
    ):
        super().__init__(name, cost, type)

    def get_pile_starting_count(self, game: "Game") -> int:
        num_players = len(game.players)
        if num_players == 1:
            return 10
        elif num_players == 2:
            return 10
        elif num_players == 3:
            return 20
        else:
            return 30

    def score(self, player: Player) -> int:
        vp = -1
        return vp


class Gardens(Victory):
    """
    Worth 1VP for every 10 cards you have (round down)

    """

    def __init__(
        self,
        name: str = "Gardens",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Victory,),
    ):
        super().__init__(name, cost, type)

    def score(self, player: Player) -> int:
        total_count = len(player.get_all_cards())
        vp = math.floor(total_count / 10)
        return vp


class Smithy(Action):
    """
    + 3 cards

    """

    def __init__(
        self,
        name: str = "Smithy",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action,),
        draw: int = 3,
    ):
        super().__init__(name, cost, type, draw=draw)


class Village(Action):
    """
    + 1 card, + 2 actions

    """

    def __init__(
        self,
        name: str = "Village",
        cost: int = 3,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 2,
        draw: int = 1,
    ):
        super().__init__(name, cost, type, actions=actions, draw=draw)


class Laboratory(Action):
    """
    +2 cards, +1 action

    """

    def __init__(
        self,
        name: str = "Laboratory",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
        draw: int = 2,
    ):
        super().__init__(name, cost, type, actions=actions, draw=draw)


class Market(Action):
    """
    +1 card, +1 action, +1 money, +1 buy

    """

    def __init__(
        self,
        name: str = "Market",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
        draw: int = 1,
        money: int = 1,
        buys: int = 1,
    ):
        super().__init__(name, cost, type, actions, draw, money, buys)


class Moneylender(Action):
    """
    You may trash a copper from your hand for + 3 money

    """

    def __init__(
        self,
        name: str = "Moneylender",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self,
        player: Player,
        game: "Game",
        generic_play: bool = True,
    ) -> None:

        super().play(player, game, generic_play)

        if copper not in player.hand.cards:
            return

        response = player.decider.binary_decision(
            prompt="Do you want to trash a copper from your hand for +3 money? y/n: ",
            card=self,
            player=player,
            game=game,
        )

        if response:
            player.trash(target_card=copper, game=game)
            player.state.money += 3


class Cellar(Action):
    """
    +1 Action

    Discard any number of cards, then draw that many

    """

    def __init__(
        self,
        name: str = "Cellar",
        cost: int = 2,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
    ):
        super().__init__(name, cost, type, actions=actions)

    def play(
        self,
        player: Player,
        game: "Game",
        generic_play: bool = True,
    ) -> None:

        super().play(player, game, generic_play)

        if not player.hand.cards:
            return

        discard_cards = player.decider.discard_decision(
            prompt="Enter the cards you would like to discard separated by commas: ",
            card=self,
            valid_cards=player.hand.cards,
            player=player,
            game=game,
        )

        for card in discard_cards:
            player.discard(game, card)
        player.draw(len(discard_cards))


class Chapel(Action):
    """
    Trash up to 4 cards from your hand

    """

    def __init__(
        self,
        name: str = "Chapel",
        cost: int = 2,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        if not player.hand.cards:
            return

        trash_cards = player.decider.trash_decision(
            prompt="Enter up to 4 cards you would like to trash from your hand: ",
            card=self,
            valid_cards=player.hand.cards,
            player=player,
            game=game,
            min_num_trash=0,
            max_num_trash=4,
        )
        assert len(trash_cards) <= 4

        for card in trash_cards:
            player.trash(card, game)


class Workshop(Action):
    """
    Gain a card costing up to 4 money

    """

    def __init__(
        self,
        name: str = "Workshop",
        cost: int = 3,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(self, player: Player, game: "Game", generic_play: bool = True) -> None:

        super().play(player, game, generic_play)

        gain_cards = player.decider.gain_decision(
            prompt="Gain a card costing up to 4 money: ",
            card=self,
            valid_cards=[
                card for card in game.supply.available_cards() if card.get_cost(player, game) <= 4
            ],
            player=player,
            game=game,
            min_num_gain=1,
            max_num_gain=1,
        )
        assert len(gain_cards) == 1
        gain_card = gain_cards[0]
        assert gain_card.get_cost(player, game) <= 4

        player.gain(gain_card, game)


class Festival(Action):
    """
    + 2 actions, + 1 buy, + 2 money

    """

    def __init__(
        self,
        name: str = "Festival",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 2,
        money: int = 2,
        buys: int = 1,
    ):
        super().__init__(name, cost, type, actions=actions, money=money, buys=buys)


class Harbinger(Action):
    """
    +1 card, +1 action

    Look through your discard pile. You may put a card from it onto your deck

    """

    def __init__(
        self,
        name: str = "Harbinger",
        cost: int = 3,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
        draw: int = 1,
    ):
        super().__init__(name, cost, type, actions=actions, draw=draw)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        if not player.discard_pile:
            return

        topdeck_cards = player.decider.topdeck_decision(
            prompt="You may select a card from your discard pile to put onto your deck: ",
            card=self,
            valid_cards=player.discard_pile.cards,
            player=player,
            game=game,
            min_num_topdeck=0,
            max_num_topdeck=1,
        )

        if len(topdeck_cards) == 0:
            return

        assert len(topdeck_cards) == 1
        topdeck_card = topdeck_cards[0]
        player.deck.add(player.discard_pile.remove(topdeck_card))


class Vassal(Action):
    """
    +2 money

    Discard the top card of your deck. If it's an action card you may play it.

    """

    def __init__(
        self,
        name: str = "Vassal",
        cost: int = 3,
        type: Tuple[CardType, ...] = (CardType.Action,),
        money: int = 2,
    ):
        super().__init__(name, cost, type, money=money)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        temp = AbstractDeck()
        player.draw(destination=temp, silent=True)

        if len(temp) == 0:
            return

        discard_card = temp.cards[0]

        player.discard(game, discard_card, temp)

        if CardType.Action not in discard_card.type:
            return

        decision = player.decider.binary_decision(
            prompt=f"You discarded {discard_card.name}, would you like to play it? (y/n): ",
            card=self,
            player=player,
            game=game,
        )

        if not decision:
            return

        played_card = player.discard_pile.cards.pop()
        player.playmat.add(played_card)
        player.exact_play(card=player.playmat.cards[-1], game=game, generic_play=False)


class Artisan(Action):
    """
    Gain a card to your hand costing up to 5 money.

    Put a card from your hand onto your deck

    """

    def __init__(
        self,
        name: str = "Artisan",
        cost: int = 6,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        gain_cards = player.decider.gain_decision(
            prompt="Gain a card costing up to 5 money: ",
            card=self,
            valid_cards=[
                card for card in game.supply.available_cards() if card.get_cost(player, game) <= 5
            ],
            player=player,
            game=game,
            min_num_gain=1,
            max_num_gain=1,
        )
        assert len(gain_cards) == 1
        gain_card = gain_cards[0]
        assert gain_card.get_cost(player, game) <= 5

        player.gain(card=gain_card, game=game, destination=player.hand)

        topdeck_cards = player.decider.topdeck_decision(
            prompt="Put a card from your hand onto your deck: ",
            card=self,
            valid_cards=player.hand.cards,
            player=player,
            game=game,
            min_num_topdeck=1,
            max_num_topdeck=1,
        )
        assert len(topdeck_cards) == 1
        topdeck_card = topdeck_cards[0]

        for card in player.hand.cards:
            if card == topdeck_card:
                player.deck.add(player.hand.remove(card))
                return


class Poacher(Action):
    """
    +1 card, +1 action, + 1 money

    Discard a card per empty Supply pile

    """

    def __init__(
        self,
        name: str = "Poacher",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
        draw: int = 1,
        money: int = 1,
    ):
        super().__init__(name, cost, type, actions, draw, money)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        empty_piles = game.supply.num_empty_piles()

        if empty_piles == 0:
            return

        discard_num = min(empty_piles, len(player.hand))

        discard_cards = player.decider.discard_decision(
            prompt=f"Discard {discard_num} card(s) from your hand: ",
            card=self,
            valid_cards=player.hand.cards,
            player=player,
            game=game,
            min_num_discard=discard_num,
            max_num_discard=discard_num,
        )
        assert len(discard_cards) == discard_num

        for discard_card in discard_cards:
            player.discard(game, discard_card)


class CouncilRoom(Action):
    """
    +4 cards, +1 buy

    Each other player draws a card

    """

    def __init__(
        self,
        name: str = "Council Room",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
        draw: int = 4,
        buys: int = 1,
    ):
        super().__init__(name, cost, type, draw=draw, buys=buys)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        for p in game.players:
            if p is not player:
                p.draw()


class Witch(Action):
    """
    +2 cards

    Each other player gains a curse

    """

    def __init__(
        self,
        name: str = "Witch",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action, CardType.Attack),
        draw: int = 2,
    ):
        super().__init__(name, cost, type, draw=draw)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        for opponent in game.players:
            if opponent is not player:
                if opponent.is_attacked(attacking_player=player, attack_card=self, game=game):

                    # attempt to gain a curse. if curse pile is empty, proceed
                    try:
                        opponent.gain(
                            card=curse,
                            game=game,
                        )
                    except EmptyPile:
                        pass


class Moat(Action):
    """
    +2 cards

    When another player plays an attack card, you may first
    reveal this from your hand, to be unaffected by it

    """

    class MoatAttackEffect(AttackEffect):
        def __init__(self, player: Player):
            super().__init__(f"Moat: {player.player_id} block attack", EffectAction.Other)
            self.player = player

        def is_triggered(self, attacking_player: Player, defending_player: Player, attack_card: Card, game: "Game") -> bool:
            return self.player.player_id == defending_player.player_id

        def handler(self, attacking_player: Player, defending_player: Player, attack_card: Card, game: "Game") -> bool:
            block = defending_player.decider.binary_decision(
                prompt=f"Would you like to block {attacking_player.player_id}'s {attack_card} with your Moat? y/n: ",
                card=moat,
                player=defending_player,
                game=game,
                relevant_cards=[attack_card],
            )
            if block:
                defending_player.reveal(moat, game)
                logger.info(f"{defending_player} blocks {attack_card} with Moat")

            return not block

    def __init__(
        self,
        name: str = "Moat",
        cost: int = 2,
        type: Tuple[CardType, ...] = (CardType.Action, CardType.Reaction),
        draw: int = 2,
    ):
        super().__init__(name, cost, type, draw=draw)

    def set_up(self, game: "Game") -> None:
        hand_add_effect = FuncPlayerCardGameEffect(
            "Moat: Hand Add",
            EffectAction.Other,
            self.on_hand_add,
            lambda p, c, g: c.name == self.name,
        )
        game.effect_registry.register_hand_add_effect(hand_add_effect)

        hand_remove_effect = FuncPlayerCardGameEffect(
            "Moat: Hand Remove",
            EffectAction.Other,
            self.on_hand_remove,
            lambda p, c, g: c.name == self.name,
        )
        game.effect_registry.register_hand_remove_effect(hand_remove_effect)

    def on_hand_add(self, player: Player, card: Card, game: "Game") -> None:
        effect = Moat.MoatAttackEffect(player)
        game.effect_registry.register_attack_effect(effect)

    def on_hand_remove(self, player: Player, card: Card, game: "Game") -> None:
        game.effect_registry.unregister_attack_effects(f"Moat: {player.player_id} block attack")


class Merchant(Action):
    """
    +1 card, +1 action

    The first time you play a Silver this turn, +1 money

    """

    MONEY_EFFECT_NAME = "Merchant: +$1"

    class MoneyEffect(PlayerCardGameEffect):
        def __init__(self):
            super().__init__(Merchant.MONEY_EFFECT_NAME)
            self.first_play = True

        def get_action(self) -> EffectAction:
            return EffectAction.Other

        def is_triggered(self, player: Player, card: Card, game: "Game") -> bool:
            return card.name == "Silver" and self.first_play

        def handler(self, player: Player, card: Card, game: "Game") -> None:
            player.state.money += 1
            self.first_play = False

    def __init__(
        self,
        name: str = "Merchant",
        cost: int = 3,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
        draw: int = 1,
    ):
        super().__init__(name, cost, type, actions=actions, draw=draw)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        money_effect = Merchant.MoneyEffect()
        game.effect_registry.register_play_effect(money_effect)

        reset_effect = FuncPlayerGameEffect("Merchant: reset", EffectAction.Other, self.remove_play_handlers)
        game.effect_registry.register_turn_end_effect(reset_effect)

    def remove_play_handlers(self, player: "Player", game: "Game") -> None:
        game.effect_registry.unregister_play_effects(self.MONEY_EFFECT_NAME)


class Bandit(Action):
    """
    Gain a Gold. Each other player reveals the top 2 cards of their deck,
    trashes a revealed treasure other than Copper, and discards the rest

    """

    def __init__(
        self,
        name: str = "Bandit",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action, CardType.Attack),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        # attempt to gain a gold. if gold pile is empty, proceed
        try:
            player.gain(card=gold, game=game)
        except EmptyPile:
            pass

        for opponent in game.players:
            if opponent is not player:
                if opponent.is_attacked(attacking_player=player, attack_card=self, game=game):

                    revealed_cards = AbstractDeck()
                    opponent.draw(num_cards=2, destination=revealed_cards, silent=True)

                    opponent.reveal(revealed_cards.cards, game)

                    trash_card = None
                    for card in revealed_cards.cards:
                        if card.name == "Silver":
                            trash_card = card
                        elif card.name == "Gold" and not trash_card:
                            trash_card = card
                        elif (
                            CardType.Treasure in card.type
                            and card.name != "Copper"
                            and not trash_card
                        ):
                            trash_card = card

                    if trash_card:
                        game.trash.add(revealed_cards.remove(trash_card))

                    revealed_cards_copy = revealed_cards.cards[:]
                    for card in revealed_cards_copy:
                        opponent.discard(game, card, revealed_cards)


class Bureaucrat(Action):
    """
    Gain a Silver onto your deck. Each other player reveals a victory card from
    their hand and puts it onto their deck (or reveals a hand with no victory cards)

    """

    def __init__(
        self,
        name: str = "Bureaucrat",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action, CardType.Attack),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        # attempt to gain a silver. if silver pile is empty, proceed
        try:
            player.gain(card=silver, game=game, destination=player.deck)
        except EmptyPile:
            pass

        for opponent in game.players:
            if opponent is not player and opponent.is_attacked(
                attacking_player=player, attack_card=self, game=game
            ):

                victory_cards = []
                for card in opponent.hand.cards:
                    if CardType.Victory in card.type:
                        victory_cards.append(card)

                if not victory_cards:
                    opponent.reveal(opponent.hand.cards, game, f"{opponent} reveals hand: ")
                    continue

                topdeck_cards = opponent.decider.topdeck_decision(
                    prompt="You must topdeck a Victory card from your hand: ",
                    card=self,
                    valid_cards=victory_cards,
                    player=opponent,
                    game=game,
                    min_num_topdeck=1,
                    max_num_topdeck=1,
                )
                assert len(topdeck_cards) == 1
                topdeck_card = topdeck_cards[0]

                opponent.deck.add(opponent.hand.remove(topdeck_card))
                opponent.reveal(topdeck_card, game, f"{opponent} reveals and topdecks ")


class ThroneRoom(Action):
    """
    You may play an Action card from your hand twice

    """

    def __init__(
        self,
        name: str = "Throne Room",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        action_cards = [card for card in player.hand.cards if CardType.Action in card.type]

        if not action_cards:
            return

        dp_card = player.decider.multi_play_decision(
            prompt="You may play an action card from your hand twice: ",
            card=self,
            valid_cards=action_cards,
            player=player,
            game=game,
            required=True,
        )
        assert dp_card is not None

        for card in player.hand.cards:
            if card.name == dp_card.name:
                player.playmat.add(player.hand.remove(card))
                state = None
                for i in range(2):
                    state = player.multi_play(card=card, game=game, state=state, generic_play=False)
                return


class Remodel(Action):
    """
    Trash a card from your hand. Gain a card costing up to $2 more than it

    """

    def __init__(
        self,
        name: str = "Remodel",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        trash_cards = player.decider.trash_decision(
            prompt="Trash a card from your hand: ",
            card=self,
            valid_cards=player.hand.cards,
            player=player,
            game=game,
            min_num_trash=1,
            max_num_trash=1,
        )
        assert len(trash_cards) == 1
        trash_card = trash_cards[0]

        max_cost = trash_card.get_cost(player, game) + 2
        gain_cards = player.decider.gain_decision(
            prompt=f"Gain a card costing up to {max_cost} money: ",
            card=self,
            valid_cards=[
                card
                for card in game.supply.available_cards()
                if card.get_cost(player, game) <= max_cost
            ],
            player=player,
            game=game,
            min_num_gain=1,
            max_num_gain=1,
        )
        assert len(gain_cards) == 1
        gain_card = gain_cards[0]
        assert gain_card.get_cost(player, game) <= max_cost

        player.trash(trash_card, game=game)
        player.gain(gain_card, game)


class Mine(Action):
    """
    You may trash a Treasure from your hand. Gain a Treasure to your hand costing up to $3 more than it

    """

    def __init__(
        self,
        name: str = "Mine",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        treasures = [card for card in player.hand.cards if CardType.Treasure in card.type]

        if not treasures:
            return

        trash_cards = player.decider.trash_decision(
            prompt="You may trash a Treasure from your hand: ",
            card=self,
            valid_cards=treasures,
            player=player,
            game=game,
            min_num_trash=0,
            max_num_trash=1,
        )

        if len(trash_cards) == 0:
            return

        assert len(trash_cards) == 1
        trash_card = trash_cards[0]

        max_cost = trash_card.get_cost(player, game) + 3
        gain_cards = player.decider.gain_decision(
            prompt=f"Gain a Treasure card costing up to {max_cost} money to your hand: ",
            card=self,
            valid_cards=[
                card
                for card in game.supply.available_cards()
                if CardType.Treasure in card.type and card.get_cost(player, game) <= trash_card.get_cost(player, game) + 3
            ],
            player=player,
            game=game,
            min_num_gain=1,
            max_num_gain=1,
        )
        assert len(gain_cards) == 1
        gain_card = gain_cards[0]
        assert CardType.Treasure in gain_card.type
        assert gain_card.get_cost(player, game) <= max_cost

        player.trash(trash_card, game=game)
        player.gain(gain_card, game, destination=player.hand)


class Militia(Action):
    """
    +2 Money

    Each other player discards down to 3 cards in hand

    """

    def __init__(
        self,
        name: str = "Militia",
        cost: int = 4,
        type: Tuple[CardType, ...] = (CardType.Action, CardType.Attack),
        money: int = 2,
    ):
        super().__init__(name, cost, type, money=money)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        for opponent in game.players:
            if opponent is not player and opponent.is_attacked(
                attacking_player=player, attack_card=self, game=game
            ):

                num_discard = len(opponent.hand) - 3
                if num_discard <= 0:
                    continue

                discard_cards = opponent.decider.discard_decision(
                    prompt=f"You must discard {num_discard} card(s) from your hand: ",
                    card=self,
                    valid_cards=opponent.hand.cards,
                    player=opponent,
                    game=game,
                    min_num_discard=num_discard,
                    max_num_discard=num_discard,
                )
                assert len(discard_cards) == num_discard

                for card in discard_cards:
                    opponent.discard(game, target_card=card)


class Sentry(Action):
    """
    +1 card, +1 action

    Look at the top 2 cards of your deck. Trash and/or discard any number of them. Put the rest back on top in any order

    """

    def __init__(
        self,
        name: str = "Sentry",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
        actions: int = 1,
        draw: int = 1,
    ):
        super().__init__(name, cost, type, actions=actions, draw=draw)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        looked_at = AbstractDeck()
        player.draw(num_cards=2, destination=looked_at, silent=True)

        trash_cards = player.decider.trash_decision(
            prompt="Enter the cards you would like to trash: ",
            card=self,
            valid_cards=looked_at.cards,
            player=player,
            game=game,
            min_num_trash=0,
            max_num_trash=2,
        )

        for card in trash_cards:
            looked_at.remove(card)

        discard_cards: List[Card] = []
        if len(looked_at.cards) > 0:
            discard_cards = player.decider.discard_decision(
                prompt="Enter the cards you would like to discard: ",
                card=self,
                valid_cards=looked_at.cards,
                player=player,
                game=game,
            )
            for card in discard_cards:
                looked_at.remove(card)

        reorder = False
        if len(looked_at.cards) == 2:
            logger.info(
                f"Current order: {looked_at.cards[0]} (Top), {looked_at.cards[1]} (Bottom)"
            )
            reorder = player.decider.binary_decision(
                prompt="Would you like to switch the order of the cards?",
                card=self,
                player=player,
                game=game,
            )

        to_trash = AbstractDeck(trash_cards[:])
        for card in trash_cards:
            player.trash(card, game, to_trash)

        to_discard = AbstractDeck(discard_cards[:])
        for card in discard_cards:
            player.discard(game, card, to_discard)

        if looked_at.cards:
            if reorder:
                for card in looked_at.cards:
                    player.deck.add(card)
            else:
                for card in reversed(looked_at.cards):
                    player.deck.add(card)
            logger.info(f"{player} topdecks {len(looked_at.cards)} cards")


class Library(Action):
    """
    Draw until you have 7 cards in hand, skipping any Action cards you choose to; set those aside, discarding them afterwards

    """

    def __init__(
        self,
        name: str = "Library",
        cost: int = 5,
        type: Tuple[CardType, ...] = (CardType.Action,),
    ):
        super().__init__(name, cost, type)

    def play(
        self, player: Player, game: "Game", generic_play: bool = True
    ) -> None:

        super().play(player, game, generic_play)

        set_aside = AbstractDeck()
        while len(player.hand) < 7:

            if len(player.deck) == 0 and len(player.discard_pile) == 0:
                return

            player.draw(num_cards=1, destination=set_aside)
            drawn_card = set_aside.cards[-1]

            if CardType.Action in drawn_card.type:
                should_skip = player.decider.binary_decision(
                    prompt=f"You drew {drawn_card}, would you like to skip it? y/n: ",
                    card=self,
                    player=player,
                    game=game,
                    relevant_cards=[drawn_card],
                )
                if not should_skip:
                    player.hand.add(set_aside.remove(drawn_card))

            else:
                player.hand.add(set_aside.remove(drawn_card))

        for card in set_aside.cards[:]:
            player.discard(game, card, set_aside)


copper = Copper()
silver = Silver()
gold = Gold()
estate = Estate()
duchy = Duchy()
province = Province()
curse = Curse()

artisan = Artisan()
bandit = Bandit()
bureaucrat = Bureaucrat()
cellar = Cellar()
chapel = Chapel()
council_room = CouncilRoom()
festival = Festival()
gardens = Gardens()
harbinger = Harbinger()
laboratory = Laboratory()
library = Library()
market = Market()
merchant = Merchant()
militia = Militia()
mine = Mine()
moat = Moat()
moneylender = Moneylender()
poacher = Poacher()
remodel = Remodel()
sentry = Sentry()
smithy = Smithy()
throne_room = ThroneRoom()
vassal = Vassal()
village = Village()
witch = Witch()
workshop = Workshop()


base_set: List[Card] = [
    artisan,
    bandit,
    bureaucrat,
    cellar,
    chapel,
    council_room,
    festival,
    gardens,
    harbinger,
    laboratory,
    library,
    market,
    merchant,
    militia,
    mine,
    moat,
    moneylender,
    poacher,
    remodel,
    sentry,
    smithy,
    throne_room,
    vassal,
    village,
    witch,
    workshop,
]
