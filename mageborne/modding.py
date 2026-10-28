"""Everything a Python mod needs, in one import:

    from modding import Monster, Player, Ability

Subclass Monster to make a monster, Player to make a character class, and Ability to make a
special move. No registering required - the game finds your classes automatically.

Ready-made abilities (Stun, Breath, Slam, Heal) and helpers (line_tiles, tiles_within) are
available too. See mods/README.md.
"""
from abilities import Ability, Breath, Heal, Slam, Stun, line_tiles, tiles_within
from monsters.monster import Monster
from player import Player

__all__ = ["Monster", "Player", "Ability", "Stun", "Breath", "Slam", "Heal",
           "line_tiles", "tiles_within"]
