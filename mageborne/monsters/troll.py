from abilities import Slam
from .monster import Monster


class Troll(Monster):
    """Boss. Telegraphs a big ground slam (dodge the red tiles!) and enrages at half HP."""
    name         = "troll"
    emoji        = "🗿"
    max_hp       = 30
    attack       = 5
    chase_radius = 8
    speed        = 2
    atk_min      = 1
    atk_max      = 1
    abilities    = [Slam(damage=12, radius=1, windup=1, range=3, cooldown=3, delay=1)]

    enraged = False

    def take_turn(self, game):
        if not self.enraged and self.hp <= self.max_hp // 2:
            self.enraged = True
            self.attack += 2
            for ability in self.abilities:
                ability.cooldown = max(1, ability.cooldown - 1)
            game.say(f"{self.emoji} The Troll roars in a rage! It hits harder and slams more often!")
        super().take_turn(game)
