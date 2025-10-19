from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List


@dataclass
class Move:
    """Simple representation of a move used by a Pokémon."""

    name: str
    power: int
    accuracy: float = 1.0

    def hits(self) -> bool:
        """Determine whether the move hits based on its accuracy."""
        roll = random.random()
        return roll <= self.accuracy


@dataclass
class Pokemon:
    """A light-weight battle ready Pokémon model."""

    name: str
    max_hp: int
    attack: int
    defense: int
    moves: List[Move]
    hp: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp = self.max_hp

    def is_fainted(self) -> bool:
        return self.hp <= 0

    def heal(self) -> None:
        self.hp = self.max_hp

    def use_move(self, move: Move, target: "Pokemon") -> str:
        """Execute a move against the target and return the outcome text."""
        if not move.hits():
            return f"{self.name}'s {move.name} missed!"

        base_damage = move.power + self.attack - target.defense
        damage = max(1, int(base_damage * random.uniform(0.85, 1.15)))
        target.receive_damage(damage)
        return f"{self.name} used {move.name}! It dealt {damage} damage."

    def receive_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)


def basic_starter() -> Pokemon:
    """Create a pre-configured starter Pokémon for the player."""
    return Pokemon(
        name="EmberFox",
        max_hp=35,
        attack=12,
        defense=8,
        moves=[
            Move("Flame Burst", power=10, accuracy=0.95),
            Move("Quick Strike", power=8, accuracy=1.0),
        ],
    )


def wild_creatures() -> List[Pokemon]:
    """Return a list of potential wild Pokémon the player can encounter."""
    return [
        Pokemon(
            name="Leaflin",
            max_hp=28,
            attack=9,
            defense=7,
            moves=[Move("Leaf Whip", power=9, accuracy=0.95)],
        ),
        Pokemon(
            name="Splashu",
            max_hp=30,
            attack=8,
            defense=9,
            moves=[Move("Bubble Pop", power=8, accuracy=0.9)],
        ),
        Pokemon(
            name="Sparkoo",
            max_hp=26,
            attack=11,
            defense=6,
            moves=[Move("Spark Shot", power=10, accuracy=0.9)],
        ),
    ]
