from .monster import Monster


class Witch(Monster):
    name         = "witch"
    emoji        = "🧙‍♀️"
    max_hp       = 9
    attack       = 7
    chase_radius = 6
    atk_min      = 4
    atk_max      = 5
