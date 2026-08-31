"""LabMaze: the same maze grid as the bloodstream level, drawn as a lab. """
from __future__ import annotations

from typing import Tuple

import pygame

from maze import Maze
from settings import (
    TILE_SIZE,
    COLOR_LAB_FLOOR,
    COLOR_LAB_FLOOR_LINE,
    COLOR_LAB_BENCH,
    COLOR_LAB_BENCH_BORDER,
)


class LabMaze(Maze):
    """A Maze that renders as a biotech lab (benches + tiled floor)."""

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        """Draws only the visible tiles."""
        ox, oy = camera_offset
        screen_w, screen_h = surface.get_size()
        col_start = max(0, ox // TILE_SIZE)
        col_end = min(self.cols, (ox + screen_w) // TILE_SIZE + 1)
        row_start = max(0, oy // TILE_SIZE)
        row_end = min(self.rows, (oy + screen_h) // TILE_SIZE + 1)

        surface.fill(COLOR_LAB_BENCH)  # fallback background grout

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                rect = pygame.Rect(col * TILE_SIZE - ox, row * TILE_SIZE - oy, TILE_SIZE, TILE_SIZE)
                if self.grid[row][col]:
                    pygame.draw.rect(surface, COLOR_LAB_BENCH, rect)
                    pygame.draw.rect(surface, COLOR_LAB_BENCH_BORDER, rect, width=2)
                else:
                    # lab flooring.
                    pygame.draw.rect(surface, COLOR_LAB_FLOOR, rect)
                    pygame.draw.rect(surface, COLOR_LAB_FLOOR_LINE, rect, width=1)