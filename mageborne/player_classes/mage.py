from player import Player


class Mage(Player):
    class_name  = "Mage"
    description = "An arcane user of magic, focusing on intelligence but with low health."
    emoji       = "🧙"

    strength     = 8
    dexterity    = 12
    constitution = 12
    intelligence = 17

    attack    = 6
    atk_range = 4
    speed     = 2
