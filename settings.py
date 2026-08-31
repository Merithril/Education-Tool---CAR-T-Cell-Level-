"""Global constants for the CAR-T Cell Maze game.

Change values here to retune the game without touching logic elsewhere.
"""

# --- Window ---
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "CAR-T Cell Maze - Level 1: Cancer Cell 1"

# --- Tiles ---
TILE_SIZE = 32

# --- General text/UI colors (R, G, B) ---
COLOR_TEXT = (240, 240, 240)
COLOR_POPUP_BG = (20, 20, 30, 230)
COLOR_POPUP_BORDER = (240, 200, 40)
COLOR_POPUP_BUTTON = (240, 200, 40)
COLOR_POPUP_BUTTON_TEXT = (20, 20, 20)

# Pop-up size, centered on screen. Enlarged from the original "quarter of
# the screen" sizing because several info texts didn't fit at 480x320 -
# combined with the word-wrap in popup.py, this comfortably fits 6-7 lines
# of body text per page.
POPUP_WIDTH = 640
POPUP_HEIGHT = 420

# --- Player: a CAR-T cell, floating freely (no gravity) in 4 directions.
# Design note: the player never takes damage and has no health bar - see
# player.py. Progress is tracked via collected CAR components instead.
PLAYER_SPEED = 4
PLAYER_SIZE = 22
COLOR_PLAYER = (70, 210, 190)          # greenish-blue, per the character brief
COLOR_PLAYER_SHOT = (150, 230, 255)    # the assembled CAR receptor's "shot" color

# How many CAR components must be collected before the receptor is complete
# and the boss-arena gate unlocks.
TOTAL_CAR_PARTS = 4
PLAYER_SHOT_SPEED = 7
PLAYER_SHOT_SIZE = 6
PLAYER_SHOT_COOLDOWN = 20  # frames between shots during the boss fight (~0.33s)

# --- Blood-vessel maze design ---
# Collision still runs on the rectangular tile grid (see maze.py is_wall);
# only the rendering is organic. Cells close to the start ("root") are
# drawn as thick "arteries", cells near dead ends as thin "capillaries".
COLOR_TISSUE_BG = (32, 8, 12)             # "tissue" outside the vessels (= wall)
COLOR_VESSEL_BASE = (140, 25, 35)          # vessel color at rest
COLOR_VESSEL_HIGHLIGHT = (255, 95, 90)     # vessel color at the pulse peak
VESSEL_MAX_RADIUS = 15.0                   # radius near the root (artery)
VESSEL_MIN_RADIUS = 5.0                    # radius at dead ends (capillary)
VESSEL_CURVE_STRENGTH = 8.0                # curvature per corridor segment, in pixels
VESSEL_PULSE_PERIOD = 260.0                # smaller = faster heartbeat
VESSEL_PULSE_WAVE = 0.12                   # how fast the pulse travels outward

# --- CAR receptor components (collectible items) ---
COLOR_ITEM_CORE = (255, 221, 120)   # bright gold - reads clearly against the red vessels
COLOR_ITEM_GLOW = (255, 200, 60)    # soft glow drawn behind the item

# --- Boss-arena gate ---
COLOR_GATE_LOCKED = (150, 60, 60)
COLOR_GATE_OPEN = (60, 180, 90)

# --- Cancer cells (both the level-1 blocker and the boss share this color -
# they are the same "enemy type" narratively) ---
COLOR_CANCER_CELL = (200, 30, 40)

# --- Drifting cell hazards ---
# Small clusters placed near some CAR components. Per the design brief the
# player takes no damage from touching them - they exist purely to make
# picking up the nearby item feel like a small maneuvering challenge.
DRIFTING_CELL_SPEED = 2
DRIFTING_CELL_SIZE = 20
COLOR_DRIFTING_CELL = (220, 80, 200)

# --- Boss: Cancer Cell 2 ---
# Has a shield pool that must be depleted before its core health can be
# damaged. Fires projectiles at the player for visual tension only (the
# player cannot be hit/damaged - see player.py).
BOSS_SIZE = 40
BOSS_SHIELD_HP = 5     # number of player shots needed to break the shield
BOSS_CORE_HP = 8       # number of further shots needed to defeat the boss
BOSS_FIRE_COOLDOWN = 70
BOSS_SHOT_SPEED = 4
BOSS_SHOT_SIZE = 8
COLOR_BOSS_SHIELD = (80, 160, 220)
COLOR_BOSS_SHOT = (255, 120, 60)
BOSS_DEFEAT_ANIM_FRAMES = 45  # shrink/fade animation length once defeated

# --- Cancer Cell 1 (the intro obstacle) ---
# The player is confined to a small box around the spawn point until this
# encounter's pop-up has been read (see main.py).
START_CONFINEMENT_TILES = 4

# =============================================================================
# THREE-SUBLEVEL REDESIGN ("Level Concept Vol. 2")
# =============================================================================
# Everything above this line belongs to the original single-level prototype
# (main.py / player.py / enemies.py) and is kept as-is so that prototype
# still runs unmodified. Everything below is used by the new level_1_*,
# level_2_*, level_3_* files, which implement the three sublevels from the
# updated concept doc: a lab item-hunt, a drag-and-drop assembly puzzle,
# and a simplified bloodstream fight against multiple cancer cells.
# =============================================================================

# --- Level 1 "Welcome to the Lab": lab visual theme ---
# LabMaze (level_1_maze.py) reuses Maze's generation/collision logic but
# renders walls as lab benches and floors as tiles instead of blood vessels.
COLOR_LAB_FLOOR = (222, 228, 232)          # light tile floor
COLOR_LAB_FLOOR_LINE = (196, 204, 210)     # thin grid line between floor tiles
COLOR_LAB_BENCH = (120, 132, 145)          # lab bench / wall color
COLOR_LAB_BENCH_BORDER = (80, 90, 100)     # bench outline, for a bit of depth
COLOR_SCIENTIST_COAT = (250, 250, 245)     # white lab coat
COLOR_SCIENTIST_ACCENT = (60, 130, 200)    # gloves/glasses accent color

# --- Level 2 "CAR Puzzle": drag-and-drop assembly ---
# Redesigned to look like an actual CAR receptor cross-section (scFv "arms"
# above a membrane, a hinge+transmembrane segment crossing it, then the
# intracellular signaling domains below) instead of plain labeled boxes.
COLOR_PUZZLE_BG = (24, 26, 34)
COLOR_OUTLINE = (90, 96, 110)              # the empty receptor outline/slots
COLOR_SLOT_CORRECT = (70, 190, 110)        # slot lights up green when solved
COLOR_SLOT_WRONG_FLASH = (210, 70, 70)     # brief red flash on a wrong drop
COLOR_TRAY_BG = (34, 37, 48)               # piece "tray" background at the bottom

# One distinct color per CAR domain, reused for its puzzle piece, its slot
# highlight, and (optionally) matching item colors in Level 1 for visual
# continuity between sublevels.
COLOR_DOMAIN_SCFV = (240, 200, 40)
COLOR_DOMAIN_HINGE_TM = (90, 190, 230)
COLOR_DOMAIN_COSTIM = (200, 120, 220)
COLOR_DOMAIN_CD3ZETA = (240, 120, 90)

PUZZLE_WRONG_FLASH_FRAMES = 20  # how long a slot flashes red on a wrong drop

# --- Cell membrane visual (drawn behind the slots, between the
# extracellular scFv "arms" and the intracellular domains) ---
COLOR_MEMBRANE_FILL = (58, 66, 92)
COLOR_MEMBRANE_LINE = (120, 150, 200)
COLOR_MEMBRANE_HEAD = (150, 178, 220)

# --- Level 3 "CAR-T Cell Fight" (simplified): multiple cancer cells ---
# No shield/shooting anymore - touching a cancer cell starts an automatic
# "binding" + dissolve animation, per the updated concept ("the player
# shortly binds to the cancer cell, which then dissolves").
CANCER_CELL_SIZE = 34
CANCER_CELL_DEFEAT_FRAMES = 30   # length of the bind/dissolve animation
COLOR_EXIT_DOOR_LOCKED = COLOR_GATE_LOCKED
COLOR_EXIT_DOOR_OPEN = COLOR_GATE_OPEN