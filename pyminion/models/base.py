from typing import List
import random

from pyminion.exceptions import (
    InsufficientMoney,
    InsufficientBuys,
    PileNotFound,
    EmptyPile,
)


class Card:
    """
    Base class representing a dominion card

    """

    def __init__(self, name: str, cost: int):
        self.name = name
        self.cost = cost

    def __repr__(self):
        return f"{self.name} ({type(self).__name__})"


class AbstractDeck:
    """
    Base class representing a generic list of dominion cards

    """

    def __init__(self, cards: List[Card] = None):
        if cards:
            self.cards = cards
        else:
            self.cards = []

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"{type(self).__name__} {[card.name for card in self.cards]}"

    def add(self, card: Card) -> Card:
        self.cards.append(card)

    def remove(self, card: Card) -> Card:
        self.cards.remove(card)
        return card


class Deck(AbstractDeck):
    def __init__(self, cards: List[Card]):
        super().__init__(cards)

    def draw(self) -> Card:
        drawn_card = self.cards.pop()
        return drawn_card

    def shuffle(self):
        random.shuffle(self.cards)

    def combine(self, cards: List[Card]):
        self.cards += cards


class DiscardPile(AbstractDeck):
    def __init__(self, cards: List[Card] = None):
        super().__init__(cards)


class Hand(AbstractDeck):
    def __init__(self, cards: List[Card] = None):
        super().__init__(cards)


class Pile(AbstractDeck):
    def __init__(self, cards: List[Card] = None):
        super().__init__(cards)
        if cards and len(set(cards)) == 1:
            self.name = cards[0].name
        elif cards:
            self.name = "Mixed"
        else:
            self.name == None

    def remove(self, card: Card) -> Card:
        if len(self.cards) < 1:
            raise EmptyPile
        self.cards.remove(card)
        return card


class Playmat(AbstractDeck):
    def __init__(self, cards: List[Card] = None):
        super().__init__(cards)


class Trash(AbstractDeck):
    def __init__(self, cards: List[Card] = None):
        super().__init__(cards)


class Player:
    """
    Collection of card piles associated with each player

    """

    def __init__(
        self,
        deck: Deck,
        discard: DiscardPile,
        hand: Hand,
        playmat: Playmat,
        player_id: str = None,
    ):
        self.deck = deck
        self.discard = discard
        self.hand = hand
        self.playmat = playmat
        self.player_id = player_id

    def draw_five(self):
        for i in range(5):  # draw 5 cards from deck and add to hand
            self.hand.add(self.deck.draw())

    def autoplay_treasures(self, turn: "Turn"):
        i = 0  # Pythonic way to pop in loop?
        while i < len(self.hand):
            if self.hand.cards[i].name == "Copper":
                self.hand.cards[i].play(turn)
            else:
                i += 1

        for card in self.hand.cards:
            if card.name == "Copper":
                card.play(turn)

    def buy(self, card: Card, turn: "Turn", supply: "Supply"):
        if card.cost > turn.money:
            raise InsufficientMoney(
                f"{turn.player.player_id}: Not enough money to buy {card.name}"
            )
        if turn.buys < 1:
            raise InsufficientBuys(
                f"{turn.player.player_id}: Not enough buys to buy {card.name}"
            )
        turn.money -= card.cost
        turn.buys -= 1
        self.discard.add(card)
        supply.gain_card(card)


class Supply:
    """
    Collection of card piles that make up the game's supply

    """

    def __init__(self, piles: List[Pile] = None):
        if piles:
            self.piles = piles
        else:
            self.piles = []

    def __len__(self):
        return len(self.piles)

    def gain_card(self, card: Card) -> Card:
        print(card.name)
        for pile in self.piles:
            print(pile.name)
            if card.name == pile.name:
                try:
                    return pile.remove(card)
                except EmptyPile:
                    print("Pile is empty, you cannot gain that card")
                    pass

        raise PileNotFound

    def return_card(self, card: Card):
        for pile in self.piles:
            if card.name == pile.name:
                pile.add(card)


class Game:
    def __init__(self, players: List[Player], supply: Supply):
        self.players = players
        self.supply = supply


class Turn:
    """
    Control state during a player's turn

    """

    def __init__(
        self,
        player: Player,
        game: Game = None,
        actions: int = 1,
        money: int = 0,
        buys: int = 1,
    ):
        self.player = player
        self.game = game
        self.actions = actions
        self.money = money
        self.buys = buys

    def clean_up(self):
        pass
