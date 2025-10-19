from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import pygame

from .battle import Battle
from .pokemon import Pokemon, basic_starter, wild_creatures

TILE_SIZE = 32
MAP_LAYOUT = [
    "####################",
    "#..............GGGG#",
    "#..####..........G.#",
    "#..#..#............#",
    "#..#..#....######..#",
    "#..#..#....#..GG#..#",
    "#..####....#..GG#..#",
    "#..........#....#..#",
    "#....GGGGGG#....#..#",
    "#....GGGGGG#....#..#",
    "#..........#....#..#",
    "#..........#....#..#",
    "#..........######..#",
    "#..................#",
    "####################",
]
MAP_WIDTH = len(MAP_LAYOUT[0])
MAP_HEIGHT = len(MAP_LAYOUT)
WINDOW_WIDTH = MAP_WIDTH * TILE_SIZE
HUD_HEIGHT = 140
WINDOW_HEIGHT = MAP_HEIGHT * TILE_SIZE + HUD_HEIGHT

COLOR_BG = (22, 26, 36)
COLOR_PANEL = (16, 18, 24)
COLOR_TEXT = (240, 240, 240)
COLOR_SHADOW = (0, 0, 0)
TILE_COLORS = {
    "#": (40, 40, 60),
    ".": (180, 170, 120),
    "G": (90, 200, 90),
}
WALKABLE_TILES = {".", "G"}


@dataclass
class Player:
    x: int
    y: int

    def move(self, dx: int, dy: int, world: "World") -> bool:
        new_x = self.x + dx
        new_y = self.y + dy
        if world.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False


class World:
    def __init__(self, layout: list[str]) -> None:
        self.layout = layout

    def is_walkable(self, x: int, y: int) -> bool:
        if x < 0 or y < 0 or y >= len(self.layout) or x >= len(self.layout[0]):
            return False
        return self.layout[y][x] in WALKABLE_TILES

    def tile_at(self, x: int, y: int) -> str:
        if 0 <= y < len(self.layout) and 0 <= x < len(self.layout[0]):
            return self.layout[y][x]
        return "#"

    def draw(self, surface: pygame.Surface) -> None:
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                color = TILE_COLORS.get(tile, (80, 80, 80))
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                surface.fill(color, rect)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Pocket Creature Adventure")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        base_font = pygame.font.get_default_font()
        self.small_font = pygame.font.Font(base_font, 18)

        self.world = World(MAP_LAYOUT)
        self.player = Player(2, 2)
        self.player_pokemon: Pokemon = basic_starter()
        self.state = "explore"
        self.battle: Optional[Battle] = None
        self.current_message: Optional[str] = None
        self.awaiting_command = False
        self.info_text = "Explore the tall grass to find wild creatures!"

    def run(self) -> None:
        running = True
        while running:
            dt = self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_key(event.key)

            self.draw()
            pygame.display.flip()

        pygame.quit()

    def handle_key(self, key: int) -> None:
        if self.state == "explore":
            self.handle_explore_key(key)
        elif self.state == "battle":
            self.handle_battle_key(key)

    def handle_explore_key(self, key: int) -> None:
        moved = False
        if key == pygame.K_UP:
            moved = self.player.move(0, -1, self.world)
        elif key == pygame.K_DOWN:
            moved = self.player.move(0, 1, self.world)
        elif key == pygame.K_LEFT:
            moved = self.player.move(-1, 0, self.world)
        elif key == pygame.K_RIGHT:
            moved = self.player.move(1, 0, self.world)

        if moved:
            if self.state == "explore":
                self.current_message = None
            tile = self.world.tile_at(self.player.x, self.player.y)
            if tile == "G" and random.random() < 0.15:
                self.start_battle()
            else:
                self.info_text = "Press arrow keys to move."

    def handle_battle_key(self, key: int) -> None:
        if self.battle is None:
            return

        if self.awaiting_command:
            move_keys = {
                pygame.K_a: 0,
                pygame.K_1: 0,
                pygame.K_KP1: 0,
                pygame.K_2: 1,
                pygame.K_KP2: 1,
                pygame.K_3: 2,
                pygame.K_KP3: 2,
                pygame.K_4: 3,
                pygame.K_KP4: 3,
            }
            if key in move_keys and self.player_pokemon.moves:
                move_index = move_keys[key]
                self.battle.player_attack(move_index)
                self.awaiting_command = False
                self.sync_battle_message()
            elif key == pygame.K_r:
                self.battle.attempt_run()
                self.awaiting_command = False
                self.sync_battle_message()
        else:
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.sync_battle_message()

    def start_battle(self) -> None:
        wild = random.choice(wild_creatures())
        wild.heal()
        self.state = "battle"
        self.battle = Battle(self.player_pokemon, wild)
        self.current_message = None
        self.awaiting_command = False
        self.sync_battle_message()

    def sync_battle_message(self) -> None:
        if self.battle is None:
            return

        while self.battle.has_messages():
            self.current_message = self.battle.pop_message()
            if self.current_message and "Choose an action" in self.current_message:
                self.awaiting_command = True
                return
            else:
                self.awaiting_command = False
                return

        if self.battle.over:
            if not self.awaiting_command:
                self.finish_battle()

    def finish_battle(self) -> None:
        if self.battle is None:
            return

        if self.battle.won:
            outcome = "You won the battle!"
            self.info_text = "Victory! Keep exploring for more encounters."
        elif getattr(self.battle, "fled", False):
            outcome = "You fled from the battle."
            self.info_text = "You fled safely. Keep exploring."
        else:
            outcome = "You were defeated but your team was healed."
            self.player_pokemon.heal()
            self.player.x, self.player.y = 2, 2
            self.info_text = "You blacked out and woke up back at town."
        self.battle = None
        self.current_message = outcome
        self.state = "explore"
        self.awaiting_command = False

    def draw(self) -> None:
        self.screen.fill(COLOR_BG)
        self.world.draw(self.screen)
        self.draw_player()
        self.draw_panel()

    def draw_player(self) -> None:
        rect = pygame.Rect(
            self.player.x * TILE_SIZE + 4,
            self.player.y * TILE_SIZE + 4,
            TILE_SIZE - 8,
            TILE_SIZE - 8,
        )
        pygame.draw.rect(self.screen, (60, 120, 255), rect, border_radius=6)

    def draw_panel(self) -> None:
        panel_rect = pygame.Rect(0, MAP_HEIGHT * TILE_SIZE, WINDOW_WIDTH, HUD_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_PANEL, panel_rect)
        pygame.draw.rect(self.screen, (80, 80, 120), panel_rect, width=3)

        if self.state == "battle":
            self.draw_battle_panel(panel_rect)
        else:
            self.draw_explore_panel(panel_rect)

    def draw_explore_panel(self, panel_rect: pygame.Rect) -> None:
        lines = [self.info_text, "Walk into the tall grass to find wild creatures."]
        for i, line in enumerate(lines):
            self.draw_text(line, 20, panel_rect.top + 20 + i * 26)
        self.draw_pokemon_status(panel_rect.top + 80)
        if self.current_message:
            self.draw_text(self.current_message, 20, panel_rect.top + 110)

    def draw_battle_panel(self, panel_rect: pygame.Rect) -> None:
        self.draw_pokemon_status(panel_rect.top + 10)
        if self.battle:
            enemy_line = f"Wild {self.battle.opponent.name} HP: {self.battle.opponent.hp}/{self.battle.opponent.max_hp}"
            self.draw_text(enemy_line, 20, panel_rect.top + 50)
            moves_line = "  ".join(
                f"[{i + 1}] {move.name}"
                for i, move in enumerate(self.player_pokemon.moves)
            )
            if moves_line:
                self.draw_text(f"Moves: {moves_line}", 20, panel_rect.top + 105)
            self.draw_text("Press [R] to attempt to run.", 20, panel_rect.top + 130)

        if self.current_message:
            self.draw_text(self.current_message, 20, panel_rect.top + 80)
        elif self.awaiting_command:
            self.draw_text("Choose an action: select a move number or press [R] to run.", 20, panel_rect.top + 80)

    def draw_pokemon_status(self, y: int) -> None:
        status = f"{self.player_pokemon.name} HP: {self.player_pokemon.hp}/{self.player_pokemon.max_hp}"
        self.draw_text(status, 20, y)

    def draw_text(self, text: str, x: int, y: int) -> None:
        shadow = self.small_font.render(text, True, COLOR_SHADOW)
        self.screen.blit(shadow, (x + 2, y + 2))
        rendered = self.small_font.render(text, True, COLOR_TEXT)
        self.screen.blit(rendered, (x, y))


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
