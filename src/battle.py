from __future__ import annotations

import random
from collections import deque
from typing import Deque, Optional

from .pokemon import Pokemon


class Battle:
    """Encapsulates a simple turn-based battle."""

    def __init__(self, player: Pokemon, opponent: Pokemon) -> None:
        self.player = player
        self.opponent = opponent
        self.messages: Deque[str] = deque(
            [
                f"A wild {self.opponent.name} appeared!",
                "Choose an action: pick a move number or press [R] to run.",
            ]
        )
        self.over = False
        self.won = False
        self.fled = False

    def has_messages(self) -> bool:
        return bool(self.messages)

    def pop_message(self) -> Optional[str]:
        if self.messages:
            return self.messages.popleft()
        return None

    def queue_message(self, message: str) -> None:
        self.messages.append(message)

    def player_attack(self, move_index: int = 0) -> None:
        if self.over:
            return

        move = self.player.moves[move_index % len(self.player.moves)]
        self.queue_message(self.player.use_move(move, self.opponent))
        if self.opponent.is_fainted():
            self.queue_message(f"Wild {self.opponent.name} fainted! You won the battle.")
            self.over = True
            self.won = True
            return
        self._opponent_turn()

    def attempt_run(self) -> None:
        if self.over:
            return

        if random.random() < 0.5:
            self.queue_message("You successfully ran away!")
            self.over = True
            self.fled = True
        else:
            self.queue_message("Couldn't escape!")
            self._opponent_turn()

    def _opponent_turn(self) -> None:
        if self.over:
            return

        move = random.choice(self.opponent.moves)
        self.queue_message(self.opponent.use_move(move, self.player))
        if self.player.is_fainted():
            self.queue_message(f"{self.player.name} fainted! You blacked out...")
            self.over = True
            self.won = False
        else:
            self.queue_message("Choose an action: pick a move number or press [R] to run.")
