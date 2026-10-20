from .monster import Monster


class Archer(Monster):
    name         = "archer"
    emoji        = "🏹"
    max_hp       = 7
    attack       = 3
    chase_radius = 5
    atk_min      = 2
    atk_max      = 3
