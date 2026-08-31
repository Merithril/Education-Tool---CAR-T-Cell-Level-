"""LabMaze: the same maze grid as the bloodstream level, drawn as a lab.

Design note: we deliberately reuse `Maze` (from maze.py) for the maze
GENERATION and COLLISION logic (the recursive-backtracker algorithm,
`is_wall`, `cell_center_px`, `carve_room`) by subclassing it - only the
RENDERING changes. This means Level 1's maze is guaranteed to behave
exactly like Level 3's maze (same "perfect maze" guarantees, same
collision rules), just drawn with lab benches and tiles instead of an
organic blood-vessel network.
"""
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
    """A Maze that renders as a biotech lab (benches + tiled floor).

    Inherits `_generate`, `is_wall`, `cell_center_px`, and `carve_room`
    unchanged from Maze. `_build_vessel_layout()` still runs in
    `Maze.__init__` (harmless - it's just unused data for this subclass),
    so we only need to override `draw()`.
    """

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        """Draws only the visible tiles, offset by the camera - same
        camera-scrolling approach as the vessel maze, just with simple
        rectangles instead of curved vessels.
        """
        ox, oy = camera_offset
        screen_w, screen_h = surface.get_size()
        col_start = max(0, ox // TILE_SIZE)
        col_end = min(self.cols, (ox + screen_w) // TILE_SIZE + 1)
        row_start = max(0, oy // TILE_SIZE)
        row_end = min(self.rows, (oy + screen_h) // TILE_SIZE + 1)

        surface.fill(COLOR_LAB_BENCH)  # fallback background (acts like "grout")

        for row in range(row_start, row_end):
            for col in range(col_start, col_end):
                rect = pygame.Rect(col * TILE_SIZE - ox, row * TILE_SIZE - oy, TILE_SIZE, TILE_SIZE)
                if self.grid[row][col]:
                    # Wall cell -> draw as a lab bench block with a border,
                    # so benches read as solid furniture rather than flat color.
                    pygame.draw.rect(surface, COLOR_LAB_BENCH, rect)
                    pygame.draw.rect(surface, COLOR_LAB_BENCH_BORDER, rect, width=2)
                else:
                    # Floor cell -> light tile with a thin grid line, like
                    # lab flooring.
                    pygame.draw.rect(surface, COLOR_LAB_FLOOR, rect)
                    pygame.draw.rect(surface, COLOR_LAB_FLOOR_LINE, rect, width=1)