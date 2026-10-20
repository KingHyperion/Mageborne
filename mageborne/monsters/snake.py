from .monster import Monster


class Snake(Monster):
    name         = "snake"
    emoji        = "🐍"
    max_hp       = 6
    attack       = 2
    chase_radius = 4
    atk_min      = 1
    atk_max      = 1
