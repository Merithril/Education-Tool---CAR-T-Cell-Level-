"""Level 3: "CAR-T Cell Fight". """
from __future__ import annotations

import sys

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_TEXT, CANCER_CELL_SCORE_TARGET
from maze import Maze
from level_3_player import BloodstreamPlayer
from level_3_enemies import CancerCell
from items import BossGate  # reused here as the level's exit door
from popup import Popup

MAZE_COLS = 29
MAZE_ROWS = 21



CANCER_CELL_CELLS = [
    (27, 1), (15, 1), (5, 3), (21, 3),
    (9, 5), (25, 5), (3, 7), (17, 7),
    (11, 9), (23, 9), (5, 11), (19, 11),
    (27, 13), (13, 13), (7, 15), (21, 15),
]
EXIT_DOOR_CELL = (27, 19)

TOTAL_CANCER_CELLS = len(CANCER_CELL_CELLS)
SCORE_TARGET = min(CANCER_CELL_SCORE_TARGET, TOTAL_CANCER_CELLS)

START_PAGES = [
    [
        "Welcome to the Bloodstream!",
        "Your CAR receptor is complete, and you're back in the",
        "patient's body, travelling through the bloodstream as a",
        "fully-armed CAR-T cell.",
    ],
    [
        "Cancer cells are drifting freely through these vessels.",
        "You'll score a point for each one you catch - reach",
        f"{SCORE_TARGET} points to unlock the exit door at the end.",
        "You don't have to catch every single one.",
    ],
]

FIRST_KILL_PAGES = [
    [
        "Target Eliminated",
        "Your CAR receptor recognized the cancer cell's surface",
        "antigen and bound to it directly - no MHC presentation",
        "needed. That triggered your signaling domains, and the",
        "cancer cell was destroyed.",
    ],
]

END_PAGES = [
    [
        "Target Score Reached!",
        "This is a simplified picture of what CAR-T cells do in a",
        "real patient: multiply, patrol the bloodstream, and",
        "destroy cancer cells that carry the target antigen - all",
        "without needing MHC presentation.",
    ],
    [
        "In real therapy, this process continues for weeks as the",
        "CAR-T cells expand in number and keep watch for relapse.",
    ],
]


def build_level(seed: int = 1) -> dict:
    maze = Maze(MAZE_COLS, MAZE_ROWS, seed=seed)
    player = BloodstreamPlayer(*maze.cell_center_px(1, 1))

    cancer_cells = [CancerCell(*maze.cell_center_px(col, row)) for col, row in CANCER_CELL_CELLS]
    exit_door = BossGate(EXIT_DOOR_CELL[0], EXIT_DOOR_CELL[1], maze)

    return {
        "maze": maze,
        "player": player,
        "cancer_cells": cancer_cells,
        "exit_door": exit_door,
        "defeated_count": 0,
        "first_kill_shown": False,
    }


def clamp_camera(player: BloodstreamPlayer, maze: Maze) -> tuple[int, int]:
    cam_x = player.x - SCREEN_WIDTH / 2
    cam_y = player.y - SCREEN_HEIGHT / 2
    cam_x = max(0, min(cam_x, maze.width_px - SCREEN_WIDTH))
    cam_y = max(0, min(cam_y, maze.height_px - SCREEN_HEIGHT))
    return int(cam_x), int(cam_y)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, defeated_count: int) -> None:
    """Score counter. """
    label = font.render(f"Score: {min(defeated_count, SCORE_TARGET)}/{SCORE_TARGET}", True, COLOR_TEXT)
    surface.blit(label, (12, 10))
    dot_radius = 8
    for i in range(SCORE_TARGET):
        filled = i < defeated_count
        cx = 20 + i * (dot_radius * 2 + 8)
        cy = 40
        color = (240, 200, 40) if filled else (70, 70, 80)
        pygame.draw.circle(surface, color, (cx, cy), dot_radius)


def run_level3(screen: pygame.Surface = None) -> bool:
    """Runs Level 3 to completion."""
    owns_display = screen is None
    if owns_display:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CAR-T Cell Maze - Level 3: CAR-T Cell Fight")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    hud_font = pygame.font.SysFont("consolas", 18)

    level = build_level(seed=1)
    active_popup = Popup(START_PAGES, font)
    level_complete = False
    quit_requested = False

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                quit_requested = True
            elif active_popup is not None and active_popup.active:
                active_popup.handle_event(event)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and level_complete:
                level = build_level(seed=1)
                active_popup = Popup(START_PAGES, font)
                level_complete = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and level_complete:
                running = False

        blocking = active_popup is not None and active_popup.active
        if not blocking and not level_complete:
            keys = pygame.key.get_pressed()
            player: BloodstreamPlayer = level["player"]
            maze: Maze = level["maze"]
            player.handle_input(keys, maze)

            # --- cancer cell "binding" kills ---
            for cell in level["cancer_cells"]:
                cell.update(maze)
                if not cell.defeated and cell.rect.colliderect(player.rect):
                    cell.start_defeat()
                    level["defeated_count"] += 1
                    if not level["first_kill_shown"]:
                        level["first_kill_shown"] = True
                        active_popup = Popup(FIRST_KILL_PAGES, font)

            # --- exit door: only actually completes the level once the
            # score target is reached; touching it earlier does nothing.
            # Not every cancer cell needs to be caught. ---
            score_reached = level["defeated_count"] >= SCORE_TARGET
            exit_door: BossGate = level["exit_door"]
            if score_reached and exit_door.rect.colliderect(player.rect) and not level_complete:
                active_popup = Popup(END_PAGES, font)
                level_complete = True

        # --- draw ---
        maze = level["maze"]
        player = level["player"]
        camera = clamp_camera(player, maze)

        maze.draw(screen, camera)
        score_reached = level["defeated_count"] >= SCORE_TARGET
        level["exit_door"].draw(screen, camera, unlocked=score_reached)
        for cell in level["cancer_cells"]:
            cell.draw(screen, camera)
        player.draw(screen, camera)

        draw_hud(screen, hud_font, level["defeated_count"])

        if active_popup is not None and active_popup.active:
            active_popup.draw(screen)
        elif level_complete:
            hint = hud_font.render("Level complete! Press [R] to replay, or [Esc] to exit.", True, COLOR_TEXT)
            screen.blit(hint, (12, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    if owns_display:
        pygame.quit()
        sys.exit()
    return quit_requested


if __name__ == "__main__":
    run_level3()