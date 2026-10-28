from player import Player


class Warrior(Player):
    class_name  = "Warrior"
    description = "A martial fighter, focusing on strength."
    emoji       = "🤺"

    strength     = 15
    dexterity    = 11
    constitution = 16
    intelligence = 8

    attack    = 7
    atk_range = 1
    speed     = 2
