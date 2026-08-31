"""Level 1: "Welcome to the Lab"."""

from __future__ import annotations

import sys

import pygame

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_TEXT
from level_1_maze import LabMaze
from level_1_player import LabPlayer
from items import CarComponent, BossGate
from popup import Popup

#Maze framework

MAZE_COLS = 27
MAZE_ROWS = 19

# Exit door position
EXIT_DOOR_CELL = (1, 17)

# ---------------------------------------------------------------------------
# Level content: position of AR components and position/timing and content of pop ups.
# ---------------------------------------------------------------------------
CAR_ITEMS = [
    {
        "key": "scfv",
        "cell": (25, 1),
        "lines": [
            "Antigen-Binding Domain (scFv)",
            "Built from the variable regions of a monoclonal antibody,",
            "this domain sits outside the cell and gives the receptor",
            "its target: it recognizes and binds a specific antigen on",
            "the cancer cell's surface.",
        ],
    },
    {
        "key": "hinge_tm",
        "cell": (13, 5),
        "lines": [
            "Hinge Region & Transmembrane Domain",
            "The hinge is a flexible linker between the scFv and the",
            "cell membrane - it gives the receptor the reach and",
            "flexibility to properly engage its target. The",
            "transmembrane domain then anchors the whole receptor in",
            "the membrane, stabilizing it.",
        ],
    },
    {
        "key": "costim",
        "cell": (3, 11),
        "lines": [
            "Costimulatory Domain",
            "Taken from a protein, it delivers a second activation",
            "signal alongside CD3-zeta. Without it, T cells activate",
            "only briefly and don't persist - this domain is what",
            "gives modern CAR-T cells lasting power.",
        ],
    },
    {
        "key": "cd3zeta",
        "cell": (23, 17),
        "lines": [
            "CD3-Zeta Signaling Domain",
            "Derived from the T-cell receptor's own CD3-zeta chain,",
            "this domain carries ITAMs that get phosphorylated once",
            "the receptor binds its target - this is the trigger that",
            "switches the T cell into attack mode.",
        ],
    },
]

WELCOME_PAGES = [
    [
        "Welcome to the Lab",
        "You're a scientist preparing a patient's own T cells for",
        "CAR-T cell therapy. These T cells were just isolated from",
        "the patient's blood via leukapheresis and shipped here.",
    ],
    [
        "Your job is to collect the four domains of the CAR",
        "receptor scattered around the lab, so they can be inserted",
        "into the T cells using a viral vector.",
    ],
]

ALL_COLLECTED_PAGES = [
    [
        "All Four Components Collected!",
        "You've gathered everything needed to build a CAR receptor:",
        "the antigen-binding domain, the hinge and transmembrane",
        "region, the costimulatory domain, and the CD3-zeta",
        "signaling domain.",
    ],
    [
        "Head to the door to move on to the assembly bench, where",
        "these pieces need to be put together in the right order to",
        "form a working receptor.",
    ],
]

END_PAGES = [
    [
        "Leaving the Lab",
        "Next stop: the assembly bench, where these pieces need to",
        "be put together in the right order to form a working",
        "receptor.",
    ],
]

TOTAL_ITEMS = len(CAR_ITEMS)


def build_level(seed: int = 1) -> dict:
    """Builds Level 1's state: the lab maze, the player, and the 4 pickups."""
    maze = LabMaze(MAZE_COLS, MAZE_ROWS, seed=seed)
    player = LabPlayer(*maze.cell_center_px(1, 1))

    items = [
        CarComponent(data["cell"][0], data["cell"][1], maze, data["key"], data["key"], data["lines"])
        for data in CAR_ITEMS
    ]

    exit_door = BossGate(EXIT_DOOR_CELL[0], EXIT_DOOR_CELL[1], maze)

    return {
        "maze": maze,
        "player": player,
        "items": items,
        "exit_door": exit_door,
        "all_collected_popup_shown": False,
    }


def clamp_camera(player: LabPlayer, maze: LabMaze) -> tuple[int, int]:
    cam_x = player.x - SCREEN_WIDTH / 2
    cam_y = player.y - SCREEN_HEIGHT / 2
    cam_x = max(0, min(cam_x, maze.width_px - SCREEN_WIDTH))
    cam_y = max(0, min(cam_y, maze.height_px - SCREEN_HEIGHT))
    return int(cam_x), int(cam_y)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, player: LabPlayer) -> None:
    """Simple collection-progress indicator."""
    label = font.render(f"CAR Parts Collected: {len(player.collected_items)}/{TOTAL_ITEMS}", True, COLOR_TEXT)
    surface.blit(label, (12, 10))
    box_size = 16
    for i in range(TOTAL_ITEMS):
        filled = i < len(player.collected_items)
        rect = pygame.Rect(12 + i * (box_size + 6), 34, box_size, box_size)
        color = (240, 200, 40) if filled else (70, 70, 80)
        pygame.draw.rect(surface, color, rect, border_radius=3)


def run_level1(screen: pygame.Surface = None) -> bool:
    """Runs Level 1 to completion.  Returns True if the player closed the window entirely, or
    False if the level just finished normally.
    """
    owns_display = screen is None
    if owns_display:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CAR-T Cell Maze - Level 1: Welcome to the Lab")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    hud_font = pygame.font.SysFont("consolas", 18)

    level = build_level(seed=1)
    active_popup = Popup(WELCOME_PAGES, font)
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
                active_popup = Popup(WELCOME_PAGES, font)
                level_complete = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and level_complete:
                running = False  # lets game_launcher.py move on to Level 2

        blocking = active_popup is not None and active_popup.active
        if not blocking and not level_complete:
            keys = pygame.key.get_pressed()
            player: LabPlayer = level["player"]
            maze: LabMaze = level["maze"]
            player.handle_input(keys, maze)

            # --- CAR component pickups: every single pickup shows its own
            # info pop-up. ---
            for item in level["items"]:
                if not item.collected and item.rect.colliderect(player.rect):
                    item.collected = True
                    player.collected_items.add(item.key)
                    active_popup = Popup(item.lines, font)

            # --- once everything is collected, show exit signs. ---
            all_collected = len(player.collected_items) >= TOTAL_ITEMS
            if all_collected and not level["all_collected_popup_shown"] and (
                active_popup is None or not active_popup.active
            ):
                level["all_collected_popup_shown"] = True
                active_popup = Popup(ALL_COLLECTED_PAGES, font)

            exit_door: BossGate = level["exit_door"]
            if all_collected and exit_door.rect.colliderect(player.rect) and not level_complete:
                active_popup = Popup(END_PAGES, font)
                level_complete = True

        # --- draw ---
        maze = level["maze"]
        player = level["player"]
        camera = clamp_camera(player, maze)
        ticks = pygame.time.get_ticks()

        maze.draw(screen, camera)
        level["exit_door"].draw(screen, camera, unlocked=len(player.collected_items) >= TOTAL_ITEMS)
        for item in level["items"]:
            item.draw(screen, camera, ticks)
        player.draw(screen, camera)

        draw_hud(screen, hud_font, player)

        if active_popup is not None and active_popup.active:
            active_popup.draw(screen)
        elif level_complete:
            hint = hud_font.render(
                "Level complete! Press [R] to replay, or [Esc] to continue.", True, COLOR_TEXT
            )
            screen.blit(hint, (12, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    if owns_display:
        pygame.quit()
        sys.exit()
    return quit_requested


if __name__ == "__main__":
    run_level1()