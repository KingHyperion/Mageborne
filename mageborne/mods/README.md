# Making mods for Mageborne

A mod is a **folder**. Put it inside this `mods` folder and start the game — that's it.
Mods can add **monsters** (with special abilities), **character classes** and **storylines**.

## Quick start (2 minutes)

1. Find the `_example_mod` folder in here and **rename it to `example_mod`** (drop the underscore).
2. Run `main.py`. You'll see `✔ Example Mod ...` at the top, a new **Paladin** class, and a new
   **adventure menu** with "The Slime Cellar" (it includes a medusa that stuns you!).
3. To make your own mod: copy `_example_mod`, give the copy a new name, delete what you don't need,
   and edit the rest.

Folders starting with `_` or `.` are ignored, so that's also how you switch a mod off.

## What goes in a mod folder

Every file is optional. Use only what you need.

```
mods/
  my_mod/
    mod.json        name, author, version (just for display)
    monsters.json   new monsters (stats + abilities)
    classes.json    new character classes
    story.json      a storyline  (or several in a "stories" folder)
    anything.py     advanced: custom monsters, classes and abilities written in Python
```

Files must sit **directly** inside your mod folder (not in another folder inside it).

## monsters.json

```json
{
  "slime": { "emoji": "🟢", "hp": 6, "attack": 2, "chase_radius": 4, "atk_min": 1, "atk_max": 1 }
}
```

| field | meaning |
|---|---|
| `emoji` | what shows on the grid. Use a plain single emoji (🐺 🧟 👻); skin tones, ❤️-style emoji and combined emoji can misalign the grid |
| `hp` | health |
| `attack` | damage per hit |
| `chase_radius` | how close you must be before it starts chasing (until then it shows as 💤 idle) |
| `atk_min` / `atk_max` | the distance range it can attack from (1 and 1 = melee, orthogonal only; 3 and 4 = ranged) |
| `speed` | tiles it walks per turn (default 1; you walk 2, a Thief walks 3) |
| `abilities` | special moves — see **Abilities** below |

The name (`"slime"`) is what stories use to place it. Leave a field out and it gets a default.

## Abilities (special monster moves)

Add an `abilities` list to a monster. Each turn, the monster uses an ability if it's ready
(off cooldown and the player is in range); using one **replaces** its normal walk-and-attack that turn.

```json
"medusa": {
  "emoji": "🐍", "hp": 16, "attack": 4, "atk_min": 2, "atk_max": 3,
  "abilities": [
    { "type": "stun", "turns": 2, "range": 4, "cooldown": 5 }
  ]
}
```

**Built-in ability types**

| type | what it does | extra settings |
|---|---|---|
| `stun` | the player misses their next turns | `turns` (default 2) |
| `breath` | breathes along a straight line through the player: hurts them if they're on it and leaves 🔥 on every tile it crossed, which hurts anyone *ending their turn* on it | `damage`, `burn_damage`, `burn_turns`, `tile_emoji` |
| `slam` | marks a 🟥 danger zone for a turn, then smashes it. Move out of the zone to dodge | `damage`, `radius`, `windup`, `warn_emoji`, `center` |
| `heal` | the monster heals itself when hurt | `amount`, `below` (e.g. `0.5` = under half HP) |

**Settings every ability has** (all optional): `cooldown` (turns between uses), `range` (the player
must be this close for it to trigger), `delay` (turns to wait before the first use), and `text`
(the message shown; `{emoji}`, `{name}`, `{damage}`, `{turns}`, `{amount}` get filled in).

`slam` has two modes: `"center": "player"` (default) puts the zone where you're standing and the monster keeps
attacking normally; `"center": "self"` makes the monster stop and smash the tiles around itself.

Abilities can be combined, e.g. a dragon that breathes fire *and* heals:

```json
"abilities": [
  { "type": "breath", "damage": 6, "burn_damage": 3, "burn_turns": 3, "range": 5, "cooldown": 3 },
  { "type": "heal", "amount": 4, "below": 0.4, "cooldown": 4 }
]
```

### Writing your own ability (Python)

Need something the built-ins can't do? Subclass `Ability` in a `.py` file. As soon as it's in your mod,
`monsters.json` can use it by name (see `_example_mod/drain.py` and the "leech" monster).

```python
from modding import Ability

class Drain(Ability):
    ability_type = "drain"                        # the name used in JSON
    PARAMS   = {**Ability.PARAMS, "amount": int}  # settings JSON may give it
    amount   = 3
    range    = 1.5
    cooldown = 3

    def use(self, monster, game):
        dealt = game.damage_player(self.amount)
        monster.hp = min(monster.max_hp, monster.hp + dealt)
        self.say(game, monster, "{emoji} {name} drains {damage} HP from you!", damage=dealt)
        self.start_cooldown()
        return True        # True = this used up the monster's turn
```

Override `can_use(monster, game)` to add conditions. Inside `use`, you control the fight through `game`:

| call | what it does |
|---|---|
| `game.say("text")` | show a message during the monsters' turn |
| `game.damage_player(n)` | hurt the player (Guard halves it); returns the damage dealt |
| `game.stun_player(turns)` | make the player skip turns |
| `game.add_hazard((x, y), "🔥", damage, turns)` | damaging tile (hurts the player if they end a turn on it) |
| `game.mark(monster, tiles, "🟥")` / `game.unmark(monster)` | show / hide a danger zone (visual only) |
| `game.dist(monster)` | distance from the monster to the player |
| `game.player_x`, `game.player_y`, `game.player_hp` | where the player is and how healthy |
| `game.monsters` | everyone in the fight |

Handy helpers: `from modding import line_tiles, tiles_within` (tiles along a line / in a square area).

## classes.json

```json
{
  "Paladin": {
    "description": "A holy knight with a sturdy build.",
    "emoji": "🦸",
    "strength": 14, "dexterity": 10, "constitution": 15, "intelligence": 10,
    "attack": 7, "atk_range": 1, "speed": 2
  }
}
```

`attack` is damage per hit, `atk_range` is how many tiles away the player can hit, `speed` is how many
tiles the player walks each turn. **Constitution is health:** max HP = 8 × level + constitution.
For reference: Warrior 7 dmg / range 1, Mage 6 / range 4, Thief 5 / range 3 and speed 3.

## story.json

A story is a set of **scenes**. Each scene shows text, then does one of three things:
`"next"` (go to another scene), `"choices"` (ask the player), or `"end"` (finish the game).

```json
{
  "title": "The Slime Cellar",
  "author": "You",
  "description": "Shown in the adventure menu.",
  "start": "start",
  "scenes": {
    "start": {
      "text": ["Hello, {name}!", "A door stands before you."],
      "next": "door"
    },
    "door": {
      "text": "What do you do?",
      "choices": [
        { "text": "Kick it down", "goto": "fight",
          "check": { "stat": "strength", "dc": 12, "fail_text": "Ow." } },
        { "text": "Walk away", "goto": "ending" }
      ]
    },
    "fight": {
      "text": "Slimes!",
      "encounter": { "slime": 2 },
      "level_up": true,
      "next": "ending"
    },
    "ending": { "text": "The end.", "end": true }
  }
}
```

**Scene fields**

| field | what it does |
|---|---|
| `text` | a string, or a list of lines. `{name}`, `{class}`, `{level}` get filled in |
| `next` | the scene to go to afterwards |
| `choices` | list of `{ "text": ..., "goto": ... }`. Letters A, B, C are added for you |
| `end` | `true` finishes the story |
| `encounter` | start a fight, e.g. `{"goblin": 3, "slime": 1}` (any built-in or mod monster, up to 32) |
| `level_up` | `true` levels the player up after the fight |

A scene needs exactly one of `next`, `choices`, `end`. A scene with `choices` can't have an
`encounter` — put the fight in the scene the choice leads to.

**Skill checks.** Add `"check"` to a choice: the game rolls a d20 + (stat ÷ 10) and the player
needs to reach `dc`. Fields: `stat` (strength, dexterity, constitution or intelligence), `dc`,
and optionally `label`, `fail_text`, `fail_goto` (scene to go to on failure; otherwise the player
just picks again).

**Optional polish:** `continue_prompt` (the "Press Enter ..." text after a scene) and
`fight_prompt` (the text before a fight).

**Balancing fights:** HP resets at the start of every fight. Each round the player walks, then acts
(Attack, Rest for 20% of max HP, or Guard to halve damage), then monsters act. Test your fights as
a few different classes. A good fight makes the player *use* Rest/Guard and dodge zones, rather than
just trade blows.

## Python mods (advanced)

Need a monster that behaves differently, or a class with special code? Add a `.py` file:

```python
from modding import Monster, Player, Stun

class Gorgon(Monster):               # becomes the monster "gorgon"
    emoji = "🐍"
    max_hp = 16
    attack = 4
    chase_radius = 6
    atk_min = 2
    atk_max = 3
    abilities = [Stun(turns=2, range=4, cooldown=5)]

class Ranger(Player):                # becomes the class "Ranger"
    description = "A sharp-eyed archer."
    emoji = "🏹"
    strength, dexterity, constitution, intelligence = 10, 15, 12, 12
    attack = 5
    atk_range = 4
```

No registering needed. For total control, override `take_turn(self, game)` on a monster
(see `_example_mod/wisp.py`, which overrides `move_toward`). Python mods run real code, so
**only install mods you trust**. JSON mods can't run code.

## When something's wrong

The game never crashes because of a mod. A bad mod is skipped and the top of the screen says
why, in plain words (file, line, what's missing, and "did you mean ...?" for typos).
Common ones: a missing comma in JSON, a `goto` pointing at a scene that doesn't exist,
a monster name that isn't defined, or a misspelled ability type or setting.

If your monster, class or ability has the same name as a built-in one (for example `"goblin"`), it
**replaces** the built-in. Mods load in alphabetical order, so later ones win. Within a mod, `.py` files
load first, so JSON can use abilities you define in Python.
