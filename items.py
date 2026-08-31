"""Collectible CAR receptor components and the boss-arena gate.

Components act as the level's "keys": once all four are collected, they
auto-assemble into a working CAR receptor (see Player.car_complete), which
unlocks the gate to the boss arena and can then be fired as a weapon.
"""
from __future__ import annotations

import math
from typing import List

import pygame

from settings import COLOR_ITEM_CORE, COLOR_ITEM_GLOW, TILE_SIZE, COLOR_GATE_LOCKED, COLOR_GATE_OPEN


class CarComponent:
    """A single collectible piece of the CAR receptor.

    `key` is a short machine-readable id (e.g. "scfv"), used to track which
    parts the player has collected. `name` and `lines` hold the
    human-readable text shown in the pickup pop-up.
    """

    def __init__(self, col: int, row: int, maze, key: str, name: str, lines: List[str]):
        self.x, self.y = maze.cell_center_px(col, row)
        self.key = key
        self.name = name
        self.lines = lines
        self.collected = False
        # Deterministic per-item phase so items don't all bob/pulse in sync.
        self._phase = (col * 13 + row * 7) % 360

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - 10), int(self.y - 10), 20, 20)

    def draw(self, surface: pygame.Surface, camera_offset, ticks: int) -> None:
        if self.collected:
            return
        ox, oy = camera_offset
        # Gentle up/down float plus a soft pulsing glow - makes pickups
        # feel alive instead of static, without adding a new mechanic.
        bob = math.sin(ticks / 300.0 + self._phase) * 4
        pulse = 0.5 + 0.5 * math.sin(ticks / 200.0 + self._phase)
        draw_x, draw_y = int(self.x - ox), int(self.y - oy + bob)

        glow_radius = 12 + int(pulse * 4)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*COLOR_ITEM_GLOW, 90), (glow_radius, glow_radius), glow_radius)
        surface.blit(glow_surface, (draw_x - glow_radius, draw_y - glow_radius))

        pygame.draw.circle(surface, COLOR_ITEM_CORE, (draw_x, draw_y), 9)


class BossGate:
    """Marks the entrance to the boss arena.

    Purely visual - the actual blocking logic (staying locked until all 4
    components are collected) is handled in main.py via a simple rect
    check, since the arena itself is just another open room in the maze
    grid rather than a separate scene.
    """

    def __init__(self, col: int, row: int, maze):
        self.x, self.y = maze.cell_center_px(col, row)

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - TILE_SIZE / 2), int(self.y - TILE_SIZE / 2), TILE_SIZE, TILE_SIZE)

    def draw(self, surface: pygame.Surface, camera_offset, unlocked: bool) -> None:
        ox, oy = camera_offset
        rect = self.rect.move(-ox, -oy)
        color = COLOR_GATE_OPEN if unlocked else COLOR_GATE_LOCKED
        pygame.draw.rect(surface, color, rect, border_radius=4)