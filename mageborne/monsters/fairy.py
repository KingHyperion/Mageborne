from .monster import Monster


class Fairy(Monster):
    name         = "fairy"
    emoji        = "🧿"
    max_hp       = 18
    attack       = 7
    chase_radius = 6
    atk_min      = 3
    atk_max      = 4
