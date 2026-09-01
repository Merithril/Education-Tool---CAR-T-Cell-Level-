"""Player character for Level 3. """
from __future__ import annotations

import pygame

from settings import PLAYER_SPEED, PLAYER_SIZE, COLOR_PLAYER


class BloodstreamPlayer:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.size / 2), int(self.y - self.size / 2), self.size, self.size)

    def handle_input(self, keys, maze) -> None:
        """Player input."""
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
        ox, oy = camera_offset
        rect = self.rect.move(-ox, -oy)
        pygame.draw.rect(surface, COLOR_PLAYER, rect, border_radius=6)