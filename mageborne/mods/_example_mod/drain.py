# A brand-new ability written in Python. Once it's here, monsters.json can use it
# by name:  { "type": "drain", "amount": 3 }   (see "leech" in monsters.json)
from modding import Ability


class Drain(Ability):
    ability_type = "drain"                       # the name used in JSON
    PARAMS   = {**Ability.PARAMS, "amount": int} # settings JSON is allowed to give it
    amount   = 3
    range    = 1.5                               # must be next to the player
    cooldown = 3

    def use(self, monster, game):
        dealt = game.damage_player(self.amount)  # hurt the player (Guard reduces it)
        monster.hp = min(monster.max_hp, monster.hp + dealt)
        self.say(game, monster, "{emoji} {name} drains {damage} HP from you!", damage=dealt)
        self.start_cooldown()
        return True                              # True = this used up the monster's turn
