"""Draggable CAR-domain pieces and their target slots, for Level 2's
drag-and-drop assembly puzzle. """


from __future__ import annotations

from typing import Optional, Tuple

import pygame

from settings import (
    PUZZLE_WRONG_FLASH_FRAMES,
    COLOR_OUTLINE, COLOR_SLOT_CORRECT, COLOR_SLOT_WRONG_FLASH, COLOR_TEXT,
)


# ---------------------------------------------------------------------------
# Shape drawing: every domain is rendered as one or more "capsules" pill /
# stadium shapes - a rounded rect whose border radius equals half its
# width
# ---------------------------------------------------------------------------

def _draw_capsule(surface: pygame.Surface, color, rect: pygame.Rect, width: int = 0) -> None:
    radius = min(rect.width, rect.height) // 2
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def _draw_scfv_shape(surface: pygame.Surface, color, rect: pygame.Rect, width: int = 0) -> None:
    """ scFv's paired loop structure."""
    connector_h = max(16, int(rect.height * 0.16))
    arm_top = rect.top + connector_h
    arm_h = rect.height - connector_h
    arm_w = max(10, int(rect.width * 0.30))
    gap = rect.width - arm_w * 2
    if gap < 6:
        gap = 6
    start_x = rect.centerx - (arm_w * 2 + gap) // 2
    arm1 = pygame.Rect(start_x, arm_top, arm_w, arm_h)
    arm2 = pygame.Rect(start_x + arm_w + gap, arm_top, arm_w, arm_h)
    _draw_capsule(surface, color, arm1, width)
    _draw_capsule(surface, color, arm2, width)
    connector = pygame.Rect(arm1.centerx, rect.top, arm2.centerx - arm1.centerx, connector_h + 10)
    pygame.draw.rect(surface, color, connector, width=width, border_radius=connector_h // 2 + 5)


def _draw_hinge_tm_shape(surface: pygame.Surface, color, rect: pygame.Rect, width: int = 0) -> None:
    """A short capsule (hinge/spacer)."""
    spacer_h = int(rect.height * 0.46)
    overlap = 6  # small overlap so the two capsules read as one connected piece
    tm_h = rect.height - spacer_h + overlap
    spacer_w = max(14, int(rect.width * 0.45))
    tm_w = max(18, int(rect.width * 0.75))
    spacer_rect = pygame.Rect(rect.centerx - spacer_w // 2, rect.top, spacer_w, spacer_h)
    tm_rect = pygame.Rect(rect.centerx - tm_w // 2, rect.top + spacer_h - overlap, tm_w, tm_h)
    _draw_capsule(surface, color, spacer_rect, width)
    _draw_capsule(surface, color, tm_rect, width)


def _draw_capsule_shape(surface: pygame.Surface, color, rect: pygame.Rect, width: int = 0) -> None:
    """A single vertical capsule filling most of the given rect - CD63. """
    capsule_w = max(20, int(rect.width * 0.6))
    capsule_rect = pygame.Rect(rect.centerx - capsule_w // 2, rect.top, capsule_w, rect.height)
    _draw_capsule(surface, color, capsule_rect, width)


_SHAPE_DRAWERS = {
    "scfv": _draw_scfv_shape,
    "hinge_tm": _draw_hinge_tm_shape,
    "capsule": _draw_capsule_shape,
}


def draw_domain_shape(surface: pygame.Surface, shape_kind: str, rect: pygame.Rect, color, width: int = 0) -> None:
    _SHAPE_DRAWERS[shape_kind](surface, color, rect, width)


class PuzzlePiece:
    """A single draggable domain piece."""

    def __init__(self, key: str, shape_kind: str, color, size: Tuple[int, int], tray_pos: Tuple[int, int]):
        self.key = key
        self.shape_kind = shape_kind
        self.color = color
        self.width, self.height = size
        # `tray_pos` is the piece's resting position in the tray (top-left
        # corner). Pieces snap back here whenever a drop doesn't succeed.
        self.tray_pos = tray_pos
        self.x, self.y = tray_pos  # current top-left position on screen
        self.dragging = False
        self.placed = False
        self._drag_offset = (0, 0)  # cursor position minus piece top-left, while dragging

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def start_drag(self, mouse_pos: Tuple[int, int]) -> None:
        self.dragging = True
        self._drag_offset = (mouse_pos[0] - self.x, mouse_pos[1] - self.y)

    def drag_to(self, mouse_pos: Tuple[int, int]) -> None:
        if self.dragging:
            self.x = mouse_pos[0] - self._drag_offset[0]
            self.y = mouse_pos[1] - self._drag_offset[1]

    def snap_to_tray(self) -> None:
        self.dragging = False
        self.x, self.y = self.tray_pos

    def snap_to_slot(self, slot: "PuzzleSlot") -> None:
        self.dragging = False
        self.placed = True
        # Center the piece inside the slot.
        self.x = slot.rect.centerx - self.width / 2
        self.y = slot.rect.centery - self.height / 2

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        draw_domain_shape(surface, self.shape_kind, self.rect, self.color, width=0)


class PuzzleSlot:
    """One target position in the receptor outline, drawn as an unfilled shape."""

    def __init__(self, key: str, shape_kind: str, top_left: Tuple[int, int], size: Tuple[int, int], caption: str):
        self.key = key
        self.shape_kind = shape_kind
        self.width, self.height = size
        self.top_left = top_left
        self.caption = caption  # small label drawn beside the slot, like a diagram callout
        self.filled = False
        self.wrong_flash_timer = 0  # counts down after a wrong drop, for a brief red flash

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.top_left[0], self.top_left[1], self.width, self.height)

    def flash_wrong(self) -> None:
        self.wrong_flash_timer = PUZZLE_WRONG_FLASH_FRAMES

    def update(self) -> None:
        if self.wrong_flash_timer > 0:
            self.wrong_flash_timer -= 1

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.filled:
            color = COLOR_SLOT_CORRECT
        elif self.wrong_flash_timer > 0:
            color = COLOR_SLOT_WRONG_FLASH
        else:
            color = COLOR_OUTLINE
        draw_domain_shape(surface, self.shape_kind, self.rect, color, width=3)

        # Caption drawn to the right of the slot, like a callout label in a
        # receptor diagram - wrapped onto two lines if it's long, so it
        # never runs off the right edge of the screen.
        words = self.caption.split(" ")
        line1, line2 = self.caption, ""
        max_chars = 30
        if len(self.caption) > max_chars:
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
        cap_x = self.rect.right + 18
        if line2:
            l1_surf = font.render(line1, True, COLOR_TEXT)
            l2_surf = font.render(line2, True, COLOR_TEXT)
            total_h = l1_surf.get_height() + l2_surf.get_height() + 2
            top = self.rect.centery - total_h // 2
            surface.blit(l1_surf, (cap_x, top))
            surface.blit(l2_surf, (cap_x, top + l1_surf.get_height() + 2))
        else:
            l1_surf = font.render(line1, True, COLOR_TEXT)
            surface.blit(l1_surf, (cap_x, self.rect.centery - l1_surf.get_height() // 2))

        # A short leader line connects the shape to its caption, echoing
        # the dotted-line callouts in a real receptor diagram.
        pygame.draw.line(surface, COLOR_OUTLINE, (self.rect.right + 4, self.rect.centery),
                          (cap_x - 4, self.rect.centery), 1)


def find_piece_at(pieces, mouse_pos: Tuple[int, int]) -> Optional[PuzzlePiece]:
    """Returns the top-most non-placed piece under the mouse, or None. """
    for piece in reversed(pieces):
        if not piece.placed and piece.rect.collidepoint(mouse_pos):
            return piece
    return None


def find_slot_at(slots, point: Tuple[int, int]) -> Optional[PuzzleSlot]:
    """Returns the slot under a given point or None."""
    for slot in slots:
        if slot.rect.collidepoint(point):
            return slot
    return None