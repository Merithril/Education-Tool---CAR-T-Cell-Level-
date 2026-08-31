"""Player character for Level 1: a scientist walking around the lab.

Simpler than the Level 3 player - no CAR receptor to fire, no health, just
movement and a record of which CAR components have been collected so far
(used to decide when the level is complete).
"""
from __future__ import annotations

from typing import Set

import pygame

from settings import PLAYER_SPEED, PLAYER_SIZE, COLOR_SCIENTIST_COAT, COLOR_SCIENTIST_ACCENT


class LabPlayer:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        # Keys of the CAR components collected so far, e.g. {"scfv", "hinge_tm"}.
        self.collected_items: Set[str] = set()

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size / 2), int(self.y - self.size / 2), self.size, self.size)

    def handle_input(self, keys, maze) -> None:
        """Move in all 4 directions - no gravity, no jumping (same movement
        rules as every other character in this game)."""
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED
        self._move(dx, 0, maze)
        self._move(0, dy, maze)

    def _move(self, dx: float, dy: float, maze) -> None:
        new_x = self.x + dx
        new_y = self.y + dy
        half = self.size / 2
        corners = [
            (new_x - half, new_y - half),
            (new_x + half - 1, new_y - half),
            (new_x - half, new_y + half - 1),
            (new_x + half - 1, new_y + half - 1),
        ]
        if not any(maze.is_wall(cx, cy) for cx, cy in corners):
            self.x = new_x
            self.y = new_y

    def draw(self, surface: pygame.Surface, camera_offset) -> None:
        """A simple stand-in sprite: a white lab-coat body with a small
        accent-colored 'safety glasses' stripe, drawn from above. Swap this
        for pygame.image.load(...) once real character art is available."""
        ox, oy = camera_offset
        rect = self.rect.move(-ox, -oy)
        pygame.draw.rect(surface, COLOR_SCIENTIST_COAT, rect, border_radius=6)
        glasses_rect = pygame.Rect(rect.x + 4, rect.y + 5, rect.width - 8, 4)
        pygame.draw.rect(surface, COLOR_SCIENTIST_ACCENT, glasses_rect, border_radius=2)