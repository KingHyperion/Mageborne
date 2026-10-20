class Player:
    """Base class for every playable class.

    Subclasses override the class attributes below to change the stat
    spread, attack damage, attack range, and emoji.
    """

    # Class-level info (overridden by subclasses)
    class_name  = "Adventurer"
    description = "A plain adventurer."
    emoji       = "🧑"

    # Base stat spread
    strength     = 10
    dexterity    = 10
    constitution = 10
    intelligence = 10

    # Combat stats
    attack    = 3
    atk_range = 1

    def __init__(self, name, level=1):
        self.name  = name
        self.level = level

    @property
    def health(self):
        return int(10 * self.level + (self.constitution / 10))

    def level_up(self):
        self.level += 1
        print(f"Congratulations! You're now level {self.level}")

    def describe(self):
        print(
            "Player description:\n"
            f" Name: {self.name}\n"
            f" Class: {self.class_name}\n"
            f" Health: {self.health}\n"
            f" Attack: {self.attack}\n"
            f" Attack Range: {self.atk_range}\n"
            f" Strength: {self.strength}\n"
            f" Dexterity: {self.dexterity}\n"
            f" Constitution: {self.constitution}\n"
            f" Intelligence: {self.intelligence}\n"
            " ========================================"
        )
