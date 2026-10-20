from player import Player


class Warrior(Player):
    class_name  = "Warrior"
    description = "A martial fighter, focusing on strength."
    emoji       = "🤺"

    strength     = 15
    dexterity    = 14
    constitution = 13
    intelligence = 8

    attack    = 4
    atk_range = 1
