from player import Player


class Mage(Player):
    class_name  = "Mage"
    description = "An arcane user of magic, focusing on intelligence but with low health."
    emoji       = "🧙"

    strength     = 8
    dexterity    = 12
    constitution = 13
    intelligence = 15

    attack    = 5
    atk_range = 5
