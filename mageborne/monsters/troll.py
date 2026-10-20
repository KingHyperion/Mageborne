from .monster import Monster


class Troll(Monster):
    name         = "troll"
    emoji        = "🧌"
    max_hp       = 20
    attack       = 6
    chase_radius = 3
    atk_min      = 1
    atk_max      = 1
