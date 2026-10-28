from .monster import Monster


class Goblin(Monster):
    name         = "goblin"
    emoji        = "👹"
    max_hp       = 8
    attack       = 4
    chase_radius = 5
    atk_min      = 1
    atk_max      = 1
