"""Special monster abilities.

An ability is a move a monster can use instead of its normal walk-and-attack, e.g. a
gaze that stuns you or a breath that sets the floor on fire. Give a monster a list of them:

    class Medusa(Monster):
        abilities = [Stun(turns=2, range=4, cooldown=5)]

...or, with no code at all, in monsters.json:

    "medusa": { ..., "abilities": [ {"type": "stun", "turns": 2, "range": 4, "cooldown": 5} ] }

Make your own by subclassing Ability (see mods/README.md). Subclasses in a mod are picked up
automatically and can be used from JSON by their `ability_type` name.
"""
import math

from config import GRID_SIZE

ABILITY_TYPES = {}          # name used in monsters.json -> Ability class
NUMBER = (int, float)


# ── Helpers for ability authors ───────────────────────────────
def line_tiles(x0, y0, x1, y1, length):
    """Tiles on a straight line from (x0, y0) through (x1, y1), up to `length` tiles
    (stops at the edge of the grid). The start tile itself is not included."""
    dx, dy = x1 - x0, y1 - y0
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return []
    tiles = []
    for i in range(1, int(length) + 1):
        x = x0 + int(math.floor(dx * i / steps + 0.5))
        y = y0 + int(math.floor(dy * i / steps + 0.5))
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            break
        tiles.append((x, y))
    return tiles


def tiles_within(x, y, radius):
    """Every tile within `radius` tiles of (x, y), diagonals included (a square area)."""
    return [(tx, ty)
            for tx in range(max(0, x - radius), min(GRID_SIZE, x + radius + 1))
            for ty in range(max(0, y - radius), min(GRID_SIZE, y + radius + 1))
            if (tx, ty) != (x, y)]


def _fill(text, **values):
    for key, value in values.items():
        text = text.replace("{" + key + "}", str(value))
    return text


# ── Base class ────────────────────────────────────────────────
class Ability:
    """Base class. Override `use()` (and `can_use()` if you want a condition).

    Settings every ability has (all optional):
        cooldown  turns to wait after using it before it can be used again
        range     the player must be within this many tiles for it to trigger
        delay     monster turns to wait before the first use
        text      the message shown when it's used ({emoji} {name} {damage} {turns} are filled in)
    """
    ability_type = None
    PARAMS   = {"cooldown": int, "range": NUMBER, "delay": int, "text": str}   # allowed settings
    cooldown = 4
    range    = 99
    delay    = 0
    text     = None

    def __init__(self, **settings):
        unknown = [k for k in settings if k not in self.PARAMS]
        if unknown:
            raise TypeError(f"{type(self).__name__} has no setting '{unknown[0]}'. "
                            f"Settings: {', '.join(self.PARAMS)}")
        for key, value in settings.items():
            setattr(self, key, value)
        self._wait = self.delay

    # -- called by the game ---------------------------------------
    def tick(self):
        if self._wait > 0:
            self._wait -= 1

    @property
    def busy(self):
        """True while the ability is in the middle of something (e.g. a wind-up)."""
        return False

    def ready(self, monster, game):
        return self._wait <= 0 and self.can_use(monster, game)

    # -- override these ----------------------------------------------
    def can_use(self, monster, game):
        return game.dist(monster) <= self.range

    def use(self, monster, game):
        """Do the thing. Return True if this used up the monster's turn
        (so it doesn't also walk/attack), False to let it carry on as normal."""
        return False

    # -- handy for subclasses --------------------------------------------
    def start_cooldown(self):
        self._wait = self.cooldown

    def say(self, game, monster, default, **values):
        game.say(_fill(self.text or default, emoji=monster.emoji, name=monster.name.title(), **values))


# ── Built-in abilities ────────────────────────────────────────
class Stun(Ability):
    """The player loses their next `turns` turns (no moving, no acting)."""
    ability_type = "stun"
    PARAMS   = {**Ability.PARAMS, "turns": int}
    turns    = 2
    range    = 4
    cooldown = 5

    def can_use(self, monster, game):
        return game.player_stunned == 0 and super().can_use(monster, game)

    def use(self, monster, game):
        game.stun_player(self.turns)
        self.say(game, monster, "{emoji} {name}'s gaze freezes you in place! You'll miss {turns} turn(s).",
                 turns=self.turns)
        self.start_cooldown()
        return True


class Breath(Ability):
    """Breathes along a straight line through the player: hurts them if they're on it
    and leaves lingering flames on every tile it crossed."""
    ability_type = "breath"
    PARAMS      = {**Ability.PARAMS, "damage": int, "burn_damage": int, "burn_turns": int, "tile_emoji": str}
    damage      = 5
    burn_damage = 2
    burn_turns  = 3
    tile_emoji  = "🔥"
    range       = 5
    cooldown    = 3

    def use(self, monster, game):
        path = line_tiles(monster.x, monster.y, game.player_x, game.player_y, self.range)
        for tile in path:
            game.add_hazard(tile, self.tile_emoji, self.burn_damage, self.burn_turns)
        dealt = game.damage_player(self.damage) if (game.player_x, game.player_y) in path else 0
        self.say(game, monster, "{emoji} {name} breathes fire! It hits you for {damage} and the flames linger.",
                 damage=dealt)
        self.start_cooldown()
        return True


class Slam(Ability):
    """A telegraphed area attack. The danger zone is shown on the grid for `windup` turns, then
    everything standing in it is hit. Move out of the zone to avoid it.

    center="player" (default): the zone appears around where YOU are standing, and the monster
        keeps walking/attacking normally in the meantime - dodging costs you your position.
    center="self": the monster stops to wind up and smashes the tiles around itself.
    """
    ability_type = "slam"
    PARAMS     = {**Ability.PARAMS, "damage": int, "radius": int, "windup": int,
                  "warn_emoji": str, "center": str}
    damage     = 8
    radius     = 1
    windup     = 1
    warn_emoji = "🟥"
    center     = "player"
    range      = 2
    cooldown   = 3

    def __init__(self, **settings):
        super().__init__(**settings)
        self._winding = 0
        self._tiles   = []

    @property
    def busy(self):
        return self._winding > 0

    def ready(self, monster, game):
        return self.busy or super().ready(monster, game)

    def _tile_center(self, monster, game):
        return (monster.x, monster.y) if self.center == "self" else (game.player_x, game.player_y)

    def use(self, monster, game):
        takes_turn = (self.center == "self")
        if not self.busy:                                   # start the wind-up
            cx, cy = self._tile_center(monster, game)
            self._tiles = tiles_within(cx, cy, self.radius) + [(cx, cy)]
            if self.center == "self":
                self._tiles.remove((cx, cy))                # the monster's own tile
            game.mark(monster, self._tiles, self.warn_emoji)
            self._winding = self.windup
            self.say(game, monster, "{emoji} {name} is about to slam the marked area! Get out of it!")
            return takes_turn
        self._winding -= 1
        if self._winding > 0:
            return takes_turn
        game.unmark(monster)                                # the slam lands
        if (game.player_x, game.player_y) in self._tiles:
            dealt = game.damage_player(self.damage)
            game.say(f"💥 The slam hits you for {dealt} damage!")
        else:
            game.say(f"{monster.emoji} The slam crashes down - and misses you!")
        self.start_cooldown()
        return takes_turn


class Heal(Ability):
    """Heals the monster itself when it's hurt."""
    ability_type = "heal"
    PARAMS   = {**Ability.PARAMS, "amount": int, "below": NUMBER}
    amount   = 3
    below    = 0.5          # only when HP is under this fraction of max
    cooldown = 3

    def can_use(self, monster, game):
        return monster.hp < monster.max_hp * self.below

    def use(self, monster, game):
        before = monster.hp
        monster.hp = min(monster.max_hp, monster.hp + self.amount)
        self.say(game, monster, "{emoji} {name} regenerates {amount} HP.", amount=monster.hp - before)
        self.start_cooldown()
        return True


for _cls in (Stun, Breath, Slam, Heal):
    ABILITY_TYPES[_cls.ability_type] = _cls
