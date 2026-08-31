"""Pop-up dialog system with pagination and a clickable "Understood" button.

Used for the level intro, the Cancer Cell 1 encounter (a short multi-slide
sequence), each CAR component pickup, and the closing recap after the
boss fight. The player can confirm either with the mouse (click the
button) or the keyboard (Enter/Space), per the concept's request for a
clickable confirmation button.
"""
from __future__ import annotations

from typing import List, Union

import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, POPUP_WIDTH, POPUP_HEIGHT,
    COLOR_POPUP_BG, COLOR_POPUP_BORDER, COLOR_TEXT,
    COLOR_POPUP_BUTTON, COLOR_POPUP_BUTTON_TEXT,
)


class Popup:
    """A modal pop-up window.

    `pages` is either a flat list of text lines (a single-page pop-up) or
    a list of pages, each itself a list of lines (a multi-slide pop-up,
    e.g. for the Cancer Cell 1 introduction).
    """

    def __init__(self, pages: Union[List[str], List[List[str]]], font: pygame.font.Font):
        if pages and isinstance(pages[0], str):
            pages = [pages]  # normalize a flat line list into a single page
        self.pages: List[List[str]] = pages
        self.page_index = 0
        self.font = font
        self.active = True
        # Recomputed every draw() call so handle_event() can compare it
        # against real mouse coordinates.
        self.button_rect = pygame.Rect(0, 0, 0, 0)

    @property
    def is_last_page(self) -> bool:
        return self.page_index >= len(self.pages) - 1

    def _advance(self) -> None:
        if self.is_last_page:
            self.active = False
        else:
            self.page_index += 1

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._advance()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                self._advance()

    def _wrap_line(self, text: str, max_width: int) -> List[str]:
        """Splits `text` into as many sub-lines as needed so each one fits
        within `max_width` pixels at the popup's font.

        This is what makes the pop-up robust to long lines: instead of
        every line list in main.py needing to be hand-wrapped to fit a
        specific box size, any text - however long - now wraps itself.
        """
        words = text.split(" ")
        lines: List[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self.font.size(candidate)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw(self, surface: pygame.Surface) -> None:
        box_w, box_h = POPUP_WIDTH, POPUP_HEIGHT
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill(COLOR_POPUP_BG)
        pygame.draw.rect(box, COLOR_POPUP_BORDER, box.get_rect(), width=3, border_radius=10)

        padding = 30
        max_text_width = box_w - padding * 2
        line_height = 30
        y = padding
        for raw_line in self.pages[self.page_index]:
            # An empty string is used as a deliberate blank spacer line
            # (see e.g. the CAR-assembly-complete pop-ups) - keep it as-is
            # instead of wrapping (which would just drop it).
            wrapped = self._wrap_line(raw_line, max_text_width) if raw_line else [""]
            for sub_line in wrapped:
                text_surf = self.font.render(sub_line, True, COLOR_TEXT)
                box.blit(text_surf, (padding, y))
                y += line_height

        if len(self.pages) > 1:
            progress = f"{self.page_index + 1} / {len(self.pages)}"
            box.blit(self.font.render(progress, True, COLOR_POPUP_BORDER), (box_w - 90, 16))

        label = "Understood" if self.is_last_page else "Next"
        button_w, button_h = 150, 40
        button_local = pygame.Rect(box_w - button_w - 24, box_h - button_h - 20, button_w, button_h)
        pygame.draw.rect(box, COLOR_POPUP_BUTTON, button_local, border_radius=8)
        label_surf = self.font.render(label, True, COLOR_POPUP_BUTTON_TEXT)
        box.blit(label_surf, label_surf.get_rect(center=button_local.center))

        origin_x, origin_y = (SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2
        surface.blit(box, (origin_x, origin_y))
        # Store the button's position in screen space (not box-local space)
        # so mouse clicks can be compared against it directly.
        self.button_rect = button_local.move(origin_x, origin_y)


class PopupTrigger:
    """An invisible zone that opens a Popup the first time the player
    enters it. Currently used for the Cancer Cell 1 encounter."""

    def __init__(self, rect: pygame.Rect, pages: Union[List[str], List[List[str]]]):
        self.rect = rect
        self.pages = pages
        self.triggered = False