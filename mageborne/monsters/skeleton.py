from .monster import Monster


class Skeleton(Monster):
    name         = "skeleton"
    emoji        = "💀"
    max_hp       = 10
    attack       = 3
    chase_radius = 3
    atk_min      = 1
    atk_max      = 1
