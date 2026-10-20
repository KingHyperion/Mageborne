from player import Player


class Thief(Player):
    class_name  = "Thief"
    description = "A cunning rogue, focusing on stealth to sneak around."
    emoji       = "🥷🏻"

    strength     = 12
    dexterity    = 15
    constitution = 13
    intelligence = 14

    attack    = 3
    atk_range = 3
