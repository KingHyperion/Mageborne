# A monster written in Python - only needed when you want custom behavior.
# (Plain stat-only monsters are easier in monsters.json.)
import random

from modding import Monster, Breath


class Wisp(Monster):          # the game finds this automatically; its name will be "wisp"
    emoji        = "🔥"
    max_hp       = 10
    attack       = 3
    chase_radius = 6
    atk_min      = 1
    atk_max      = 2
    abilities    = [Breath(damage=3, burn_damage=2, burn_turns=2, range=4, cooldown=4, tile_emoji="🔶")]

    def move_toward(self, px, py, occupied):
        # Wisps flit about: half the time they drift toward you, half the time they hang back
        if random.random() < 0.5:
            super().move_toward(px, py, occupied)
