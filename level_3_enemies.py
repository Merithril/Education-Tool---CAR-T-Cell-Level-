"""CancerCell: a single target in Level 3's bloodstream fight.

Simplified from the earlier single-boss design: there's no shield, no
health bar, and no shooting anymore. Per the updated concept ("the player
shortly binds to the cancer cell, which then dissolves"), touching a
cancer cell immediately starts a short bind/dissolve animation and counts
as a kill.

Cancer cells are small and wander the maze on their own - a simple
random-walk that respects walls the same way the player's movement does
(see `_blocked`): they keep moving in their current direction until they'd
hit a wall, or occasionally just change direction at random, so they
don't march in perfectly straight lines forever.
"""
from __future__ import annotations

import random

import pygame

from settings import (
    CANCER_CELL_SIZE, CANCER_CELL_DEFEAT_FRAMES, COLOR_CANCER_CELL,
    CANCER_CELL_SPEED, CANCER_CELL_TURN_CHANCE,
)

_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class CancerCell:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.defeated = False
        self.defeat_timer = CANCER_CELL_DEFEAT_FRAMES
        dx, dy = random.choice(_DIRECTIONS)
        self.vx, self.vy = dx * CANCER_CELL_SPEED, dy * CANCER_CELL_SPEED

    @property
    def rect(self) -> pygame.Rect:
        s = CANCER_CELL_SIZE
        return pygame.Rect(int(self.x - s / 2), int(self.y - s / 2), s, s)

    @property
    def defeat_animation_done(self) -> bool:
        """True once the shrink/dissolve animation has fully played out."""
        return self.defeated and self.defeat_timer <= 0

    def start_defeat(self) -> None:
        """Called once, the moment the player's CAR-T cell touches this
        cancer cell. Idempotent - calling it again while already defeated
        does nothing."""
        self.defeated = True

    def _blocked(self, x: float, y: float, maze) -> bool:
        """Same corner-based wall check the player uses, so cancer cells
        can't clip through walls either."""
        half = CANCER_CELL_SIZE / 2
        corners = [
            (x - half, y - half),
            (x + half - 1, y - half),
            (x - half, y + half - 1),
            (x + half - 1, y + half - 1),
        ]
        return any(maze.is_wall(cx, cy) for cx, cy in corners)

    def _pick_new_direction(self, maze) -> None:
        """Picks a random direction that isn't immediately blocked, so the
        cell doesn't get stuck pressed against a wall."""
        options = _DIRECTIONS[:]
        random.shuffle(options)
        for dx, dy in options:
            look_x = self.x + dx * CANCER_CELL_SPEED * 3
            look_y = self.y + dy * CANCER_CELL_SPEED * 3
            if not self._blocked(look_x, look_y, maze):
                self.vx, self.vy = dx * CANCER_CELL_SPEED, dy * CANCER_CELL_SPEED
                return
        self.vx = self.vy = 0.0  # boxed in on all sides - shouldn't normally happen

    def update(self, maze=None) -> None:
        if self.defeated:
            if self.defeat_timer > 0:
                self.defeat_timer -= 1
            return
        if maze is None:
            return
        new_x, new_y = self.x + self.vx, self.y + self.vy
        if self._blocked(new_x, new_y, maze) or random.random() < CANCER_CELL_TURN_CHANCE:
            self._pick_new_direction(maze)
            new_x, new_y = self.x + self.vx, self.y + self.vy
            if self._blocked(new_x, new_y, maze):
                return  # boxed in this frame - just wait
        self.x, self.y = new_x, new_y

    def draw(self, surface: pygame.Surface, camera_offset) -> None:
        if self.defeat_animation_done:
            return  # fully dissolved - nothing left to draw
        ox, oy = camera_offset
        scale = max(0.0, self.defeat_timer / CANCER_CELL_DEFEAT_FRAMES) if self.defeated else 1.0
        radius = int((CANCER_CELL_SIZE / 2) * scale)
        if radius <= 0:
            return
        pygame.draw.circle(surface, COLOR_CANCER_CELL, (int(self.x - ox), int(self.y - oy)), radius)