import os

# ── Folders ───────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODS_DIR    = os.path.join(BASE_DIR, "mods")      # drop mod folders in here
STORIES_DIR = os.path.join(BASE_DIR, "stories")   # built-in storylines
SAVES_DIR   = os.path.join(BASE_DIR, "saves")     # save files (created when you first save)

# ── Tile emojis ───────────────────────────────────────────────
FLOOR = "🟫"

# ── Config ────────────────────────────────────────────────────
GRID_SIZE     = 6
MOVE_BUDGET   = 2
REST_HEAL     = 3      # Rest always heals at least this much...
REST_HEAL_PCT = 0.2    # ...or this fraction of max HP, whichever is more
