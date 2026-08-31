"""Maze generation and rendering in the blood-vessel style. """


from __future__ import annotations

import math
import random
from collections import deque
from typing import Dict, List, Optional, Tuple

import pygame

from settings import (
    TILE_SIZE,
    COLOR_TISSUE_BG,
    COLOR_VESSEL_BASE,
    COLOR_VESSEL_HIGHLIGHT,
    VESSEL_MAX_RADIUS,
    VESSEL_MIN_RADIUS,
    VESSEL_CURVE_STRENGTH,
    VESSEL_PULSE_PERIOD,
    VESSEL_PULSE_WAVE,
)

Cell = Tuple[int, int]


def _hash_noise(x: int, y: int, seed: int) -> float:
    """Deterministic pseudo-noise in [-1, 1] for a cell coordinate."""
    n = (x * 374761393 + y * 668265263 + seed * 982451653) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    n = (n ^ (n >> 16)) & 0xFFFFFFFF
    return (n / 0xFFFFFFFF) * 2.0 - 1.0


class Maze:
    def __init__(self, cols: int, rows: int, seed: Optional[int] = None):
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.rows = rows if rows % 2 == 1 else rows + 1
        self._seed = seed if seed is not None else random.randint(0, 999_999)
        random.seed(self._seed)
        # True = wall (= tissue), False = walkable path (= vessel)
        self.grid = [[True] * self.cols for _ in range(self.rows)]
        self._generate()
        self.width_px = self.cols * TILE_SIZE
        self.height_px = self.rows * TILE_SIZE
        self._build_vessel_layout()

    def _generate(self) -> None:
        """Recursive backtracker: generates maze."""
        stack = [(1, 1)]
        self.grid[1][1] = False
        while stack:
            cx, cy = stack[-1]
            neighbours = []
            for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
                nx, ny = cx + dx, cy + dy
                if 0 < nx < self.cols - 1 and 0 < ny < self.rows - 1 and self.grid[ny][nx]:
                    neighbours.append((nx, ny, dx, dy))
            if neighbours:
                nx, ny, dx, dy = random.choice(neighbours)
                self.grid[cy + dy // 2][cx + dx // 2] = False
                self.grid[ny][nx] = False
                stack.append((nx, ny))
            else:
                stack.pop()

    def carve_room(self, cx: int, cy: int, w: int, h: int) -> None:
        """Opens up a rectangular room, e.g. for a hazard cluster or the
        boss arena."""
        for y in range(cy, cy + h):
            for x in range(cx, cx + w):
                if 0 <= y < self.rows and 0 <= x < self.cols:
                    self.grid[y][x] = False
        self._build_vessel_layout()

    def is_wall(self, world_x: float, world_y: float) -> bool:
        col = int(world_x // TILE_SIZE)
        row = int(world_y // TILE_SIZE)
        if col < 0 or row < 0 or col >= self.cols or row >= self.rows:
            return True
        return self.grid[row][col]

    def cell_center_px(self, col: int, row: int) -> Tuple[int, int]:
        return col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2

    # ------------------------------------------------------------------
    # Blood-vessel layout
    # ------------------------------------------------------------------
    def _build_vessel_layout(self) -> None:
        """Computes nodes and edges as a vessel network."""
        adjacency: Dict[Cell, List[Cell]] = {}
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col]:
                    continue
                neighbours = []
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = col + dx, row + dy
                    if 0 <= nx < self.cols and 0 <= ny < self.rows and not self.grid[ny][nx]:
                        neighbours.append((nx, ny))
                adjacency[(col, row)] = neighbours

        # BFS distance from the root (start cell) -> basis for the tapering
        root: Cell = (1, 1) if not self.grid[1][1] else next(iter(adjacency), (1, 1))
        distances: Dict[Cell, int] = {root: 0}
        queue = deque([root])
        while queue:
            cell = queue.popleft()
            for neighbour in adjacency.get(cell, []):
                if neighbour not in distances:
                    distances[neighbour] = distances[cell] + 1
                    queue.append(neighbour)
        max_dist = max(distances.values()) if distances else 1
        max_dist = max_dist or 1

        def radius_for(cell: Cell) -> float:
            dist = distances.get(cell, max_dist)
            t = dist / max_dist
            return VESSEL_MAX_RADIUS - (VESSEL_MAX_RADIUS - VESSEL_MIN_RADIUS) * t

        # Nodes: (x, y, radius, distance)
        self.vessel_nodes: List[Tuple[int, int, float, int]] = []
        for cell, dist in distances.items():
            cx, cy = self.cell_center_px(*cell)
            self.vessel_nodes.append((cx, cy, radius_for(cell), dist))

        # Edges: (points for a slightly curved line, width, distance)
        self.vessel_edges: List[Tuple[List[Tuple[float, float]], float, float]] = []
        seen_edges = set()
        for cell, neighbours in adjacency.items():
            if cell not in distances:
                continue
            for neighbour in neighbours:
                if neighbour not in distances:
                    continue
                edge_key = tuple(sorted((cell, neighbour)))
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)

                x1, y1 = self.cell_center_px(*cell)
                x2, y2 = self.cell_center_px(*neighbour)
                dx, dy = x2 - x1, y2 - y1
                length = math.hypot(dx, dy) or 1.0
                perp_x, perp_y = -dy / length, dx / length
                offset = _hash_noise(cell[0] + neighbour[0], cell[1] + neighbour[1], self._seed)
                offset *= VESSEL_CURVE_STRENGTH
                mx = (x1 + x2) / 2 + perp_x * offset
                my = (y1 + y2) / 2 + perp_y * offset

                width = radius_for(cell) + radius_for(neighbour)
                avg_dist = (distances[cell] + distances[neighbour]) / 2
                self.vessel_edges.append(([(x1, y1), (mx, my), (x2, y2)], width, avg_dist))

    def _pulse_color(self, dist: float, ticks: int) -> Tuple[int, int, int]:
        phase = (ticks / VESSEL_PULSE_PERIOD) - dist * VESSEL_PULSE_WAVE
        t = 0.5 + 0.5 * math.sin(phase)
        r = int(COLOR_VESSEL_BASE[0] + (COLOR_VESSEL_HIGHLIGHT[0] - COLOR_VESSEL_BASE[0]) * t)
        g = int(COLOR_VESSEL_BASE[1] + (COLOR_VESSEL_HIGHLIGHT[1] - COLOR_VESSEL_BASE[1]) * t)
        b = int(COLOR_VESSEL_BASE[2] + (COLOR_VESSEL_HIGHLIGHT[2] - COLOR_VESSEL_BASE[2]) * t)
        return (r, g, b)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[int, int]) -> None:
        """Draws the vessel network - the background moves with the camera."""
        ox, oy = camera_offset
        screen_w, screen_h = surface.get_size()
        view_rect = pygame.Rect(ox - 40, oy - 40, screen_w + 80, screen_h + 80)
        ticks = pygame.time.get_ticks()

        surface.fill(COLOR_TISSUE_BG)

        for points, width, avg_dist in self.vessel_edges:
            if not any(view_rect.collidepoint(p) for p in points):
                continue
            shifted = [(int(px - ox), int(py - oy)) for px, py in points]
            color = self._pulse_color(avg_dist, ticks)
            pygame.draw.lines(surface, color, False, shifted, max(2, int(width)))

        for cx, cy, radius, dist in self.vessel_nodes:
            if not view_rect.collidepoint((cx, cy)):
                continue
            color = self._pulse_color(dist, ticks)
            pygame.draw.circle(surface, color, (int(cx - ox), int(cy - oy)), max(2, int(radius)))