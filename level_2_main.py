"""Level 2: "CAR Puzzle". """


from __future__ import annotations

import sys
from typing import List

import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_TEXT, COLOR_PUZZLE_BG, COLOR_TRAY_BG,
    COLOR_DOMAIN_SCFV, COLOR_DOMAIN_HINGE_TM, COLOR_DOMAIN_COSTIM, COLOR_DOMAIN_CD3ZETA,
    COLOR_MEMBRANE_FILL, COLOR_MEMBRANE_LINE, COLOR_MEMBRANE_HEAD,
)
from level_2_pieces import PuzzlePiece, PuzzleSlot, find_piece_at, find_slot_at
from popup import Popup

# ---------------------------------------------------------------------------
# The four CAR domains, in their biologically correct outside-to-inside
# order.
# ---------------------------------------------------------------------------
DOMAINS = [
    {
        "key": "scfv",
        "shape_kind": "scfv",
        "size": (90, 120),
        "color": COLOR_DOMAIN_SCFV,
        "caption": "Targeting element (scFv) - binds the antigen outside the cell",
        "correct_lines": [
            "Correct! Antigen-Binding Domain (scFv)",
            "This piece sits at the very outside of the receptor. It's",
            "the only part that actually touches the cancer cell -",
            "everything else exists to support and transmit what",
            "happens here.",
        ],
    },
    {
        "key": "hinge_tm",
        "shape_kind": "hinge_tm",
        "size": (60, 90),
        "color": COLOR_DOMAIN_HINGE_TM,
        "caption": "Spacer & transmembrane domain - crosses the membrane",
        "correct_lines": [
            "Correct! Hinge & Transmembrane Domain",
            "This piece connects the outside to the inside: the hinge",
            "gives the scFv room to move, while the transmembrane",
            "domain locks the whole receptor into the cell membrane",
            "so it can't be lost.",
        ],
    },
    {
        "key": "costim",
        "shape_kind": "capsule",
        "size": (50, 75),
        "color": COLOR_DOMAIN_COSTIM,
        "caption": "Costimulatory domain - just inside the membrane",
        "correct_lines": [
            "Correct! Costimulatory Domain",
            "Placed just inside the membrane, this domain works",
            "together with the next one to fully activate the T cell -",
            "binding the antigen alone isn't enough without it.",
        ],
    },
    {
        "key": "cd3zeta",
        "shape_kind": "capsule",
        "size": (50, 75),
        "color": COLOR_DOMAIN_CD3ZETA,
        "caption": "CD3-zeta signaling domain - innermost",
        "correct_lines": [
            "Correct! CD3-Zeta Signaling Domain",
            "The innermost piece. Once the receptor binds its target",
            "outside the cell, this domain fires the signal that tells",
            "the T cell: attack now.",
        ],
    },
]

# --- Fixed vertical layout (top-to-bottom). ---
SLOT_CENTER_X = 330
SLOT_TOPS = {
    "scfv": 65,
    "hinge_tm": 180,
    "costim": 280,
    "cd3zeta": 365,
}

MEMBRANE_TOP = 210
MEMBRANE_BOTTOM = 245
MEMBRANE_LEFT = 60
MEMBRANE_RIGHT = 365  # stops just past the hinge_tm slot, before the caption column starts

TRAY_TOP = 460

START_PAGES = [
    [
        "Assemble the CAR Receptor",
        "Time to put the four pieces together. Real CAR receptors",
        "are built in a specific order, from the outside of the cell",
        "to the inside - drag each domain onto the outline to find",
        "out where it belongs.",
    ],
]

WRONG_PAGES = [
    ["Oops! That's not correct.", "Please try again!"],
]

END_PAGES = [
    [
        "CAR Receptor Complete!",
        "Outside to inside: antigen-binding domain, hinge and",
        "transmembrane domain, costimulatory domain, CD3-zeta",
        "signaling domain. Together, they let an engineered T cell",
        "recognize and destroy cancer cells - without needing MHC",
        "presentation at all.",
    ],
]

TOTAL_DOMAINS = len(DOMAINS)


def build_slots() -> List[PuzzleSlot]:
    """shadow frame of the domains. """
    slots = []
    for domain in DOMAINS:
        top = SLOT_TOPS[domain["key"]]
        w, h = domain["size"]
        top_left = (SLOT_CENTER_X - w // 2, top)
        slots.append(PuzzleSlot(domain["key"], domain["shape_kind"], top_left, domain["size"], domain["caption"]))
    return slots


def build_pieces() -> List[PuzzlePiece]:
    """Puzzle pieces."""
    tray_order = [DOMAINS[3], DOMAINS[1], DOMAINS[0], DOMAINS[2]]  # cd3zeta, hinge_tm, scfv, costim
    x_positions = [60, 220, 380, 560]
    pieces = []
    for domain, x in zip(tray_order, x_positions):
        pos = (x, TRAY_TOP)
        pieces.append(PuzzlePiece(domain["key"], domain["shape_kind"], domain["color"], domain["size"], pos))
    return pieces


def draw_tray_background(surface: pygame.Surface) -> None:
    tray_rect = pygame.Rect(0, TRAY_TOP - 10, SCREEN_WIDTH, SCREEN_HEIGHT - (TRAY_TOP - 10))
    pygame.draw.rect(surface, COLOR_TRAY_BG, tray_rect)


def draw_membrane(surface: pygame.Surface) -> None:
    """ simplified phospholipid-bilayer """
    band_rect = pygame.Rect(MEMBRANE_LEFT, MEMBRANE_TOP, MEMBRANE_RIGHT - MEMBRANE_LEFT, MEMBRANE_BOTTOM - MEMBRANE_TOP)
    pygame.draw.rect(surface, COLOR_MEMBRANE_FILL, band_rect)
    pygame.draw.line(surface, COLOR_MEMBRANE_LINE, (MEMBRANE_LEFT, MEMBRANE_TOP), (MEMBRANE_RIGHT, MEMBRANE_TOP), 2)
    pygame.draw.line(surface, COLOR_MEMBRANE_LINE, (MEMBRANE_LEFT, MEMBRANE_BOTTOM), (MEMBRANE_RIGHT, MEMBRANE_BOTTOM), 2)
    # Small "lipid head" dots along both edges, evenly spaced.
    head_spacing = 18
    head_radius = 4
    x = MEMBRANE_LEFT + head_spacing // 2
    while x < MEMBRANE_RIGHT:
        pygame.draw.circle(surface, COLOR_MEMBRANE_HEAD, (x, MEMBRANE_TOP), head_radius)
        pygame.draw.circle(surface, COLOR_MEMBRANE_HEAD, (x, MEMBRANE_BOTTOM), head_radius)
        x += head_spacing


def run_level2(screen: pygame.Surface = None) -> bool:
    """Runs Level 2. """
    owns_display = screen is None
    if owns_display:
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("CAR-T Cell Maze - Level 2: CAR Puzzle")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    label_font = pygame.font.SysFont("consolas", 16)
    hud_font = pygame.font.SysFont("consolas", 18)

    slots = build_slots()
    pieces = build_pieces()
    dragged_piece: PuzzlePiece = None

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
                # While a pop-up is open, all mouse/keyboard input goes to
                # it - no dragging happens "underneath" a pop-up.
                active_popup.handle_event(event)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and level_complete:
                running = False  # lets game_launcher.py move on to Level 3

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not level_complete:
                dragged_piece = find_piece_at(pieces, event.pos)
                if dragged_piece is not None:
                    dragged_piece.start_drag(event.pos)

            elif event.type == pygame.MOUSEMOTION and dragged_piece is not None:
                dragged_piece.drag_to(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragged_piece is not None:
                target_slot = find_slot_at(slots, dragged_piece.rect.center)
                if target_slot is not None and not target_slot.filled and target_slot.key == dragged_piece.key:
                    # Correct drop.
                    dragged_piece.snap_to_slot(target_slot)
                    target_slot.filled = True
                    domain = next(d for d in DOMAINS if d["key"] == dragged_piece.key)
                    all_filled = all(s.filled for s in slots)
                    if all_filled:
                        # Combine this domain's pop-up with the closing
                        # pop-up so the player doesn't have to click
                        # through two separate windows back-to-back.
                        active_popup = Popup([domain["correct_lines"]] + END_PAGES, font)
                        level_complete = True
                    else:
                        active_popup = Popup(domain["correct_lines"], font)
                elif target_slot is not None and not target_slot.filled:
                    # Wrong domain dropped on a slot.
                    target_slot.flash_wrong()
                    dragged_piece.snap_to_tray()
                    active_popup = Popup(WRONG_PAGES, font)
                else:
                    # Dropped outside any slot, or onto an already-filled
                    # slot - just return it to the tray, no pop-up needed.
                    dragged_piece.snap_to_tray()
                dragged_piece = None

        for slot in slots:
            slot.update()

        # --- draw ---
        screen.fill(COLOR_PUZZLE_BG)
        draw_membrane(screen)
        draw_tray_background(screen)
        for slot in slots:
            slot.draw(screen, label_font)
        for piece in pieces:
            piece.draw(screen, label_font)

        progress = sum(1 for s in slots if s.filled)
        hud_label = hud_font.render(f"Domains Placed: {progress}/{TOTAL_DOMAINS}", True, COLOR_TEXT)
        screen.blit(hud_label, (12, 10))

        if active_popup is not None and active_popup.active:
            active_popup.draw(screen)
        elif level_complete:
            hint = hud_font.render(
                "Puzzle complete! Press [Esc] to continue.", True, COLOR_TEXT
            )
            screen.blit(hint, (12, SCREEN_HEIGHT - 150))

        pygame.display.flip()

    if owns_display:
        pygame.quit()
        sys.exit()
    return quit_requested


if __name__ == "__main__":
    run_level2()


if __name__ == "__main__":
    run_level2()