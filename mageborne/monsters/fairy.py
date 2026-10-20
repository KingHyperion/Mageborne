from .monster import Monster


class Fairy(Monster):
    name         = "fairy"
    emoji        = "🧿"
    max_hp       = 8
    attack       = 5
    chase_radius = 6
    atk_min      = 3
    atk_max      = 4
