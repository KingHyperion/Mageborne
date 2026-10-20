from .monster import Monster


class Dragon(Monster):
    name         = "dragon"
    emoji        = "🐉"
    max_hp       = 25
    attack       = 8
    chase_radius = 6
    atk_min      = 2
    atk_max      = 5
