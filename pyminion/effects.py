from enum import IntEnum, unique
from typing import TYPE_CHECKING, Callable, Iterable, List, Optional, Union

if TYPE_CHECKING:
    from pyminion.core import Card
    from pyminion.game import Game
    from pyminion.player import Player


PlayerGameEffectHandler = Callable[["Player", "Game"], None]
PlayerGameEffectTriggerHandler = Callable[["Player", "Game"], bool]
PlayerCardGameEffectHandler = Callable[["Player", "Card", "Game"], None]
PlayerCardGameEffectTriggerHandler = Callable[["Player", "Card", "Game"], bool]


@unique
class EffectOrderType(IntEnum):
    Hidden = 0
    OrderRequired = 1
    OrderNotRequired = 2


class Effect:
    def get_order(self) -> EffectOrderType:
        raise NotImplementedError("Effect get_order is not implemented")


class PlayerGameEffect(Effect):
    def __init__(self, name: str):
        self.name = name

    def is_triggered(self, player: "Player", game: "Game") -> bool:
        raise NotImplementedError("PlayerGameEffect is_triggered is not implemented")

    def handler(self, player: "Player", game: "Game") -> None:
        raise NotImplementedError("PlayerGameEffect handler is not implemented")


class FuncPlayerGameEffect(PlayerGameEffect):
    def __init__(
        self,
        name: str,
        order: EffectOrderType,
        handler_func: PlayerGameEffectHandler,
        is_triggered_func: Optional[PlayerGameEffectTriggerHandler] = None,
    ):
        super().__init__(name)
        self._order = order
        self.handler_func = handler_func

        self.is_triggered_func: PlayerGameEffectTriggerHandler
        if is_triggered_func is None:
            self.is_triggered_func = lambda p, g: True
        else:
            self.is_triggered_func = is_triggered_func

    def get_order(self) -> EffectOrderType:
        return self._order

    def is_triggered(self, player: "Player", game: "Game") -> bool:
        return self.is_triggered_func(player, game)

    def handler(self, player: "Player", game: "Game") -> None:
        self.handler_func(player, game)


class PlayerCardGameEffect(Effect):
    def __init__(self, name: str):
        self.name = name

    def is_triggered(self, player: "Player", card: "Card", game: "Game") -> bool:
        raise NotImplementedError("PlayerCardGameEffect is_triggered is not implemented")

    def handler(self, player: "Player", card: "Card", game: "Game") -> None:
        raise NotImplementedError("PlayerCardGameEffect handler is not implemented")


class FuncPlayerCardGameEffect(PlayerCardGameEffect):
    def __init__(
        self,
        name: str,
        order: EffectOrderType,
        handler_func: PlayerCardGameEffectHandler,
        is_triggered_func: Optional[PlayerCardGameEffectTriggerHandler] = None,
    ):
        super().__init__(name)
        self._order = order
        self.handler_func = handler_func

        self.is_triggered_func: PlayerCardGameEffectTriggerHandler
        if is_triggered_func is None:
            self.is_triggered_func = lambda p, c, g: True
        else:
            self.is_triggered_func = is_triggered_func

    def get_order(self) -> EffectOrderType:
        return self._order

    def is_triggered(self, player: "Player", card: "Card", game: "Game") -> bool:
        return self.is_triggered_func(player, card, game)

    def handler(self, player: "Player", card: "Card", game: "Game") -> None:
        self.handler_func(player, card, game)


class AttackEffect(Effect):
    def __init__(self, name: str, order: EffectOrderType):
        self.name = name
        self._order = order

    def get_order(self) -> EffectOrderType:
        return self._order

    def is_triggered(self, attacking_player: "Player", defending_player: "Player", attack_card: "Card", game: "Game") -> bool:
        raise NotImplementedError("AttackEffect handler is not implemented")

    def handler(self, attacking_player: "Player", defending_player: "Player", attack_card: "Card", game: "Game") -> bool:
        raise NotImplementedError("AttackEffect handler is not implemented")


class EffectRegistry:
    """
    Registry for effects to be triggered on various game events.

    """
    def __init__(self):
        self.attack_effects: List[AttackEffect] = []
        self.buy_effects: List[PlayerCardGameEffect] = []
        self.discard_effects: List[PlayerCardGameEffect] = []
        self.gain_effects: List[PlayerCardGameEffect] = []
        self.hand_add_effects: List[PlayerCardGameEffect] = []
        self.hand_remove_effects: List[PlayerCardGameEffect] = []
        self.play_effects: List[PlayerCardGameEffect] = []
        self.reveal_effects: List[PlayerCardGameEffect] = []
        self.shuffle_effects: List[PlayerGameEffect] = []
        self.trash_effects: List[PlayerCardGameEffect] = []
        self.turn_start_effects: List[PlayerGameEffect] = []
        self.turn_end_effects: List[PlayerGameEffect] = []
        self.cleanup_start_effects: List[PlayerGameEffect] = []

    def _handle_player_game_effects(
            self,
            effects: Iterable[PlayerGameEffect],
            player: "Player",
            game: "Game",
    ) -> None:
        # sort effects by type
        hidden: List[PlayerGameEffect] = []
        order_required: List[PlayerGameEffect] = []
        order_not_required: List[PlayerGameEffect] = []
        for effect in effects:
            if effect.is_triggered(player, game):
                if effect.get_order() == EffectOrderType.Hidden:
                    hidden.append(effect)
                elif effect.get_order() == EffectOrderType.OrderRequired:
                    order_required.append(effect)
                elif effect.get_order() == EffectOrderType.OrderNotRequired:
                    order_not_required.append(effect)

        # hidden effects always happen first
        for effect in hidden:
            effect.handler(player, game)

        if len(order_required) == 0:
            for effect in order_not_required:
                effect.handler(player, game)
        else:
            combined = order_required + order_not_required
            if len(combined) == 1:
                combined[0].handler(player, game)
            else:
                # ask user to specify order
                combined = order_required + order_not_required
                order = player.decider.effects_order_decision(
                    [e.name for e in combined],
                    player,
                    game,
                )
                assert len(order) == len(set(order)) == len(combined)

                for idx in order:
                    combined[idx].handler(player, game)

    def _handle_player_card_game_effects(
            self,
            effects: Iterable[PlayerCardGameEffect],
            player: "Player",
            card: "Card",
            game: "Game",
    ) -> None:
        # sort effects by type
        hidden: List[PlayerCardGameEffect] = []
        order_required: List[PlayerCardGameEffect] = []
        order_not_required: List[PlayerCardGameEffect] = []
        for effect in effects:
            if effect.is_triggered(player, card, game):
                if effect.get_order() == EffectOrderType.Hidden:
                    hidden.append(effect)
                elif effect.get_order() == EffectOrderType.OrderRequired:
                    order_required.append(effect)
                elif effect.get_order() == EffectOrderType.OrderNotRequired:
                    order_not_required.append(effect)

        # hidden effects always happen first
        for effect in hidden:
            effect.handler(player, card, game)

        if len(order_required) == 0:
            for effect in order_not_required:
                effect.handler(player, card, game)
        else:
            # ask user to specify order
            combined = order_required + order_not_required
            if len(combined) == 1:
                combined[0].handler(player, card, game)
            else:
                order = player.decider.effects_order_decision(
                    [e.name for e in combined],
                    player,
                    game,
                )
                assert len(order) == len(set(order)) == len(combined)

                for idx in order:
                    combined[idx].handler(player, card, game)

    def _unregister_effects(
            self,
            name: str,
            effect_list: Union[List[PlayerGameEffect], List[PlayerCardGameEffect], List[AttackEffect]],
            max_unregister: int,
    ) -> None:
        unregister_count = 0
        i = 0
        while i < len(effect_list) and (max_unregister < 0 or unregister_count < max_unregister):
            effect = effect_list[i]
            if effect.name == name:
                effect_list.pop(i)
                unregister_count += 1
            else:
                i += 1

    def on_attack(self, attacking_player: "Player", defending_player: "Player", attack_card: "Card", game: "Game") -> bool:
        """
        Trigger attacking effects.

        """
        attacked = True

        # sort effects by type
        hidden: List[AttackEffect] = []
        order_required: List[AttackEffect] = []
        order_not_required: List[AttackEffect] = []
        for effect in self.attack_effects:
            if effect.is_triggered(attacking_player, defending_player, attack_card, game):
                if effect.get_order() == EffectOrderType.Hidden:
                    hidden.append(effect)
                elif effect.get_order() == EffectOrderType.OrderRequired:
                    order_required.append(effect)
                elif effect.get_order() == EffectOrderType.OrderNotRequired:
                    order_not_required.append(effect)

        # hidden effects always happen first
        for effect in hidden:
            attacked &= effect.handler(attacking_player, defending_player, attack_card, game)

        if len(order_required) == 0:
            for effect in order_not_required:
                attacked &= effect.handler(attacking_player, defending_player, attack_card, game)
        else:
            combined = order_required + order_not_required
            if len(combined) == 1:
                attacked &= combined[0].handler(attacking_player, defending_player, attack_card, game)
            else:
                # ask user to specify order
                order = defending_player.decider.effects_order_decision(
                    [e.name for e in combined],
                    defending_player,
                    game,
                )
                assert len(order) == len(set(order)) == len(combined)

                for idx in order:
                    attacked &= combined[idx].handler(attacking_player, defending_player, attack_card, game)

        return attacked

    def on_buy(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger buying effects.

        """
        self._handle_player_card_game_effects(self.gain_effects + self.buy_effects, player, card, game)

    def on_discard(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger discarding effects.

        """
        self._handle_player_card_game_effects(self.discard_effects, player, card, game)

    def on_gain(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger gaining effects.

        """
        self._handle_player_card_game_effects(self.gain_effects, player, card, game)

    def on_hand_add(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger hand adding effects.

        """
        self._handle_player_card_game_effects(self.hand_add_effects, player, card, game)

    def on_hand_remove(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger hand removing effects.

        """
        self._handle_player_card_game_effects(self.hand_remove_effects, player, card, game)

    def on_play(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger playing effects.

        """
        self._handle_player_card_game_effects(self.play_effects, player, card, game)

    def on_reveal(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger revealing effects.

        """
        self._handle_player_card_game_effects(self.reveal_effects, player, card, game)

    def on_shuffle(self, player: "Player", game: "Game") -> None:
        """
        Trigger shuffling effects.

        """
        self._handle_player_game_effects(self.shuffle_effects, player, game)

    def on_trash(self, player: "Player", card: "Card", game: "Game") -> None:
        """
        Trigger trashing effects.

        """
        self._handle_player_card_game_effects(self.trash_effects, player, card, game)

    def on_turn_start(self, player: "Player", game: "Game") -> None:
        """
        Trigger turn start effects.

        """
        self._handle_player_game_effects(self.turn_start_effects, player, game)

    def on_turn_end(self, player: "Player", game: "Game") -> None:
        """
        Trigger turn end effects.

        """
        self._handle_player_game_effects(self.turn_end_effects, player, game)

    def on_cleanup_start(self, player: "Player", game: "Game") -> None:
        """
        Trigger clean-up start effects.

        """
        self._handle_player_game_effects(self.cleanup_start_effects, player, game)

    def register_attack_effect(self, effect: AttackEffect) -> None:
        """
        Register an effect to be triggered on attacking.

        """
        self.attack_effects.append(effect)

    def unregister_attack_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on attacking.

        """
        self._unregister_effects(name, self.attack_effects, max_unregister)

    def register_buy_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on buying.

        """
        self.buy_effects.append(effect)

    def unregister_buy_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on buying.

        """
        self._unregister_effects(name, self.buy_effects, max_unregister)

    def register_discard_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on discarding.

        """
        self.discard_effects.append(effect)

    def unregister_discard_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on discarding.

        """
        self._unregister_effects(name, self.discard_effects, max_unregister)

    def register_gain_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on gaining.

        """
        self.gain_effects.append(effect)

    def unregister_gain_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on gaining.

        """
        self._unregister_effects(name, self.gain_effects, max_unregister)

    def register_hand_add_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on hand adding.

        """
        self.hand_add_effects.append(effect)

    def unregister_hand_add_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on hand adding.

        """
        self._unregister_effects(name, self.hand_add_effects, max_unregister)

    def register_hand_remove_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on hand removing.

        """
        self.hand_remove_effects.append(effect)

    def unregister_hand_remove_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on hand removing.

        """
        self._unregister_effects(name, self.hand_remove_effects, max_unregister)

    def register_play_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on playing.

        """
        self.play_effects.append(effect)

    def unregister_play_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on playing.

        """
        self._unregister_effects(name, self.play_effects, max_unregister)

    def register_reveal_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on revealing.

        """
        self.reveal_effects.append(effect)

    def unregister_reveal_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on revealing.

        """
        self._unregister_effects(name, self.reveal_effects, max_unregister)

    def register_shuffle_effect(self, effect: PlayerGameEffect) -> None:
        """
        Register an effect to be triggered on shuffling.

        """
        self.shuffle_effects.append(effect)

    def unregister_shuffle_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on shuffling.

        """
        self._unregister_effects(name, self.shuffle_effects, max_unregister)

    def register_trash_effect(self, effect: PlayerCardGameEffect) -> None:
        """
        Register an effect to be triggered on trashing.

        """
        self.trash_effects.append(effect)

    def unregister_trash_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on trashing.

        """
        self._unregister_effects(name, self.trash_effects, max_unregister)

    def register_turn_start_effect(self, effect: PlayerGameEffect) -> None:
        """
        Register an effect to be triggered on turn start.

        """
        self.turn_start_effects.append(effect)

    def unregister_turn_start_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on turn start.

        """
        self._unregister_effects(name, self.turn_start_effects, max_unregister)

    def register_turn_end_effect(self, effect: PlayerGameEffect) -> None:
        """
        Register an effect to be triggered on turn end.

        """
        self.turn_end_effects.append(effect)

    def unregister_turn_end_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on turn end.

        """
        self._unregister_effects(name, self.turn_end_effects, max_unregister)

    def register_cleanup_start_effect(self, effect: PlayerGameEffect) -> None:
        """
        Register an effect to be triggered on clean-up start.

        """
        self.cleanup_start_effects.append(effect)

    def unregister_cleanup_start_effects(self, name: str, max_unregister: int = -1) -> None:
        """
        Unregister an effect from being triggered on clean-up start.

        """
        self._unregister_effects(name, self.cleanup_start_effects, max_unregister)
