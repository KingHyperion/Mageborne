from abilities import Breath
from .monster import Monster


class Dragon(Monster):
    name         = "dragon"
    emoji        = "🐉"
    max_hp       = 25
    attack       = 8
    chase_radius = 6
    atk_min      = 2
    atk_max      = 5
    abilities    = [Breath(damage=6, burn_damage=3, burn_turns=3, range=5, cooldown=3)]
