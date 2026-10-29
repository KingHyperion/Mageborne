# Mageborne

A turn-based, text-mode RPG played on a small emoji grid, written in plain Python with no dependencies.
You pick a class, walk through a story, and fight monsters in tactical grid battles where positioning,
healing and dodging matter.

The game **saves your progress automatically**, so you can quit any time and pick up where you left off.

The whole game is **moddable**: anyone can add monsters (including ones with special abilities),
character classes and full storylines by dropping a folder into `mods/`. No code is needed for most mods,
and a built-in **template generator** creates the starter files for you.

```
🤺🟫🟫🟫🟫🟫      Turn 3  |  ❤️  HP: 24/40  |  ⚔️  ATK: 7  |  🎯 Range: 1  |  👾 Remaining: 1
🟫🟫🟫🟫🟫🟫
🟫🟫🟫🟥🟥🟥      🟥 Danger zone - Troll is about to strike there!
🟫🟫🟫🟥🗿🟥
🟫🟫🟫🟥🟥🟥
🟫🟫🟫🟫🟫🟫
```

---

## Contents

1. [Quick start](#quick-start)
2. [How to play](#how-to-play)
   - [Saving and continuing](#saving-and-continuing)
3. [Classes](#classes)
4. [Monsters](#monsters)
5. [The built-in story](#the-built-in-story)
6. [Project layout](#project-layout)
7. [How it works](#how-it-works)
8. [Modding](#modding)
   - [Generating a mod template](#generating-a-mod-template)
9. [Configuration](#configuration)
10. [Balance notes](#balance-notes)
11. [Troubleshooting](#troubleshooting)
12. [Extending the base game](#extending-the-base-game)

---

## Quick start

**Requirements:** Python 3.8 or newer, and a terminal/console that can display emoji.
There is nothing to install.

**Run it** (any of these):

- **From an editor:** open the `mageborne` folder in VS Code, Thonny, PyCharm, etc., open `main.py`, and press **Run**.
- **By double-clicking** `main.py`, if your system opens `.py` files with Python. The game needs a console window to draw the grid.
- **From a terminal:** `python main.py` (or `python3 main.py`) inside the `mageborne` folder.

You'll see a menu: **New game**, **Continue** (only if you have saves), **Create a mod template**, and **Quit**.
Starting a new game asks you to choose a class and name your character, and then the story begins.

**Adding mods needs no terminal either:** copy a mod folder into `mods/` using your file manager and start the game again.
To make your own, choose **Create a mod template** in the menu (see [Generating a mod template](#generating-a-mod-template)).

---

## How to play

### The grid

Fights happen on a **6×6 grid**. You start in the top-left corner; monsters are placed randomly everywhere except the
2×2 corner around you. Tile legend:

| Symbol | Meaning |
|---|---|
| 🟫 | empty floor |
| your class emoji | you (🤺 Warrior, 🧙 Mage, 🥷 Thief, …) |
| monster emoji | a monster (👹 goblin, 🧿 fairy, 🗿 troll, …) |
| 🟥 | **danger zone**: a monster is about to hit these tiles, so get out |
| 🔥 | **fire**: ending your turn standing on it hurts |
| 💤 (below the grid) | monsters that are idle: too far away to notice you yet |
| 💫 (below the grid) | you are stunned and will skip turns |

### A round

Each round has three phases:

1. **Move.** Walk up to your **speed** in tiles (2 for most classes, 3 for the Thief) with **W / A / S / D**.
   Press **Enter** to stop early. You can't walk through monsters.
2. **Action.** Choose one:
   - **`1` Attack:** hit a monster within your attack range. If several are in range, you choose which.
   - **`2` Rest:** heal 20% of your max HP (at least 3).
   - **`3` Guard:** take half damage from everything until your next turn.
   - Anything else: do nothing.
3. **Monsters act.** Each one uses a special ability if it has one ready, otherwise it walks toward you and attacks
   if you're in its range. Then lingering fire burns anyone standing in it.

You win when every monster is defeated. If your HP reaches 0 the game ends. **HP is fully restored at the start of each fight.**

### Saving and continuing

- **Autosave:** the game saves at the start of every story scene, so closing the window never loses more than the scene you were in.
- **Save and quit:** at any choice menu, type **`SAVE`** to save and leave cleanly.
- **Continue:** pick **Continue** in the main menu to choose a save. It resumes at the scene you were on, with the same class, name and level.
- **Losing a fight** doesn't lose progress: your last checkpoint is the start of that fight, so **Continue** lets you retry it.
- **One save per character name.** Starting a new game with a name that already has a save asks before replacing it.
- **Finished adventures** are marked `[finished]` in the Continue list and can't be resumed. Start a new game to play again.
- Saves are small JSON files in the `saves/` folder (created the first time you save). Delete a file there to delete that save.
- If a save needs a mod that isn't installed (a story or class), Continue tells you what's missing instead of crashing. Put the mod back and it works again.

### Distance and range

Distance is measured in straight lines (so a diagonal step counts as about 1.41 tiles). Two consequences:

- **Melee (range 1) only works orthogonally**: up, down, left, right. A monster standing diagonally to you can't hit you, and you can't hit it.
- Ranged attackers (Mage, Thief, archers, fairies…) work at any angle within their range.

Monsters have a **chase radius**. Until you come within it, a monster stays put and is shown as 💤 idle.

### Stats and health

| Stat | What it does |
|---|---|
| **Constitution** | your health: max HP = `8 × level + constitution` |
| **Intelligence** | adds to skill checks such as the story's "search for clues" (see below) |
| **Strength / Dexterity** | used by skill checks in stories that call for them (mods can use them freely) |
| **Attack** | damage per hit |
| **Attack range** | how many tiles away you can hit |
| **Speed** | how many tiles you can walk per round |

You level up after story fights that award it (the built-in story takes you from level 1 to 3). Levelling raises max HP.

### Skill checks

Some story choices roll a **d20 + (stat ÷ 10)**. You need to reach the target number. For example, "search for clues" needs 14 using
Intelligence. If you fail you can try a different approach.

---

## Classes

| Class | Emoji | Attack | Range | Speed | Str / Dex / Con / Int | HP at level 1 / 2 / 3 |
|---|---|---|---|---|---|---|
| **Warrior**: a martial fighter, focusing on strength | 🤺 | 7 | 1 | 2 | 15 / 11 / 16 / 8 | 24 / 32 / 40 |
| **Mage**: an arcane user of magic, focusing on intelligence | 🧙 | 6 | 4 | 2 | 8 / 12 / 12 / 17 | 20 / 28 / 36 |
| **Thief**: a cunning rogue, focusing on stealth | 🥷 | 5 | 3 | 3 | 12 / 15 / 13 / 14 | 21 / 29 / 37 |

- The **Warrior** hits hardest and has the most health, but has to stand next to things.
- The **Mage** can fight from a distance but is the most fragile.
- The **Thief** is the fastest, which helps it dodge danger zones and reposition.

---

## Monsters

All monsters walk 1 tile per round unless noted. "Attack range" is the distance band they attack from; they back away if you get closer than the minimum.

| Monster | Emoji | HP | Damage | Chase radius | Attack range | Notes |
|---|---|---|---|---|---|---|
| **Goblin** | 👹 | 8 | 4 | 5 | 1 – 1 | basic melee |
| **Archer** | 🏹 | 7 | 3 | 5 | 2 – 3 | ranged; keeps its distance |
| **Fairy** | 🧿 | 18 | 7 | 6 | 3 – 4 | ranged; keeps its distance |
| **Skeleton** | 💀 | 10 | 3 | 3 | 1 – 1 | melee |
| **Snake** | 🐍 | 6 | 2 | 4 | 1 – 1 | melee |
| **Witch** | 🔮 | 9 | 7 | 6 | 4 – 5 | long-range caster |
| **Dragon** | 🐉 | 25 | 8 | 6 | 2 – 5 | **Fire breath:** 6 damage in a line through you, and leaves 🔥 for 3 turns (cooldown 3) |
| **Troll** | 🗿 | 30 | 5 | 8 | 1 – 1 | moves 2 tiles/round. **Ground pound** (see below); **enrages** at half HP |

### The Troll fight

The troll is the boss of the built-in story:

- **Ground pound:** it marks a 3×3 area of 🟥 around where you're standing, then smashes it on its next turn for **12 damage**. It keeps
  attacking normally in the meantime, so dodging means giving up your position. You can also Guard to halve the hit.
- **Enrage:** at half HP it roars, hits 2 harder, and pounds more often.
- It always chases you and is as fast as you are, so you can't just run away and heal for free.

---

## The built-in story

**Mageborne: The Emberpine Woods** is a short three-chapter adventure. You've been hired by the townspeople of Emberpine to investigate
the woods after huge monster tracks were found.

1. **Goblins.** Search for clues (an Intelligence check), follow the trail, or try to lure a monster out. All paths lead to 3 goblins.
2. **Fairies.** Inspect the goblin footprints or keep searching. Either way, 2 fairies are waiting.
3. **The Troll.** Inspect the fairy footprints or keep searching, then face the troll boss.

You go from level 1 to level 3 along the way. The story lives in `stories/emberpine.json`, and it uses exactly the same format that mods use.

---

## Project layout

```
mageborne/
├── main.py             Entry point: main menu, new game, continue, mod template maker, command-line options
├── game.py             The battle system (grid, turns, combat, hazards, rendering)
├── story.py            Story engine: loads, checks and plays story JSON files
├── abilities.py        Monster abilities: Stun, Breath, Slam, Heal (+ the Ability base class)
├── player.py           Player base class (stats, health formula, stat sheet)
├── mod_loader.py       Finds and loads everything in mods/, with friendly error reports
├── mod_template.py     Generates a ready-to-edit mod folder (menu option and --new-mod)
├── savegame.py         Writing, listing and loading save files
├── modding.py          The one import mod authors need: Monster, Player, Ability, helpers
├── ui.py               Small shared helpers: clear screen, menus, input validation
├── config.py           Grid size, tile emoji, rest healing, folder locations
│
├── player_classes/     One file per class
│   ├── __init__.py     PLAYER_CLASSES registry (class name → class)
│   ├── warrior.py
│   ├── mage.py
│   └── thief.py
│
├── monsters/           One file per monster
│   ├── monster.py      Monster base class (movement, attacking, turn logic)
│   ├── registry.py     MONSTER_TYPES registry (name → class)
│   ├── spawner.py      Places monsters on the grid for an encounter
│   └── goblin.py  archer.py  fairy.py  skeleton.py  snake.py  witch.py  dragon.py  troll.py
│
├── stories/
│   └── emberpine.json  The built-in story
│
├── mods/
│   ├── README.md       Full modding guide
│   └── _example_mod/   A working example (rename to example_mod to enable)
│
└── saves/              Your save files (created the first time the game saves)
```

---

## How it works

### Startup

1. `main.py` calls `load_content()` from `mod_loader.py`.
2. Built-in stories in `stories/` are loaded, then each folder in `mods/` (alphabetically; folders starting with `_` or `.` are skipped).
3. After everything is loaded, every story is **checked**: scene links, monster names, encounter sizes and so on. Broken ones are skipped with an explanation.
4. If any mods were found, a short report is shown (`✔` loaded, `⚠` problem).
5. The main menu appears. **New game** asks for an adventure (only if more than one exists), a class and a name; **Continue** rebuilds the story, player and scene from a save file.
6. `run_story()` plays the story, and each fight scene starts a battle in `game.py`.

### Registries

Two dictionaries hold the content, and mods simply add to them:

- `MONSTER_TYPES` (`monsters/registry.py`): monster name → class (e.g. `"goblin"` → `Goblin`)
- `PLAYER_CLASSES` (`player_classes/__init__.py`): class name → class

A third, `ABILITY_TYPES` (`abilities.py`), maps ability names (`"stun"`, `"breath"`, …) to ability classes so JSON can refer to them.
Adding a new entry to any registry makes it appear in the game automatically (the class menu, story encounters and so on are built from them).

### Players and monsters are classes

`Player` and `Monster` are base classes holding default stats and shared logic. Every class and monster is a small subclass that only
overrides what's different:

```python
class Goblin(Monster):
    name         = "goblin"
    emoji        = "👹"
    max_hp       = 8
    attack       = 4
    chase_radius = 5
    atk_min      = 1
    atk_max      = 1
```

### The battle loop (`game.py`)

`Game` owns the battle state: the grid, the player's position and HP, the monsters, fire tiles, and danger zones. Each round:

```
player_turn()   →  move (WASD)
action_phase()  →  attack / rest / guard
monster_turn()  →  every monster runs take_turn(game), then fire ticks
```

If you're stunned, the first two steps are skipped. `Game` also exposes a small "toolbox" (`say`, `damage_player`, `stun_player`,
`add_hazard`, `mark`, `dist`, …) that abilities and custom monsters use to affect the fight. Logic and printing are kept separate enough that
the battle can be driven by a script (this is how the game was balance-tested).

### Monster turns and abilities

`Monster.take_turn(game)` does the following:

1. Tick down every ability's cooldown.
2. Try each ability. The first one that is ready and in range is used, and that **replaces** the normal move and attack for the turn.
   (An ability that's mid-wind-up always goes first.)
3. Otherwise: walk toward the player (up to `speed` tiles) and attack if in range.

Built-in abilities:

| Ability | Effect |
|---|---|
| `stun` | the player skips their next N turns |
| `breath` | damages the player along a line and leaves lingering fire on every tile it crossed |
| `slam` | marks a danger zone, then hits everything in it a turn later |
| `heal` | the monster heals itself when hurt |

Hazards (fire) are created "fresh" and only start hurting the following round, so a breath doesn't hit you twice in one turn.

### The story engine (`story.py`)

A story is JSON: a set of named **scenes**. Each scene shows text and may start a fight, then continues in exactly one of three ways:
`next` (go to another scene), `choices` (ask the player), or `end`. Choices can include a skill check. The engine validates stories
before they're playable (dead ends, links to scenes that don't exist, unknown monsters, too many monsters for the grid, misspelled fields
with "did you mean…?" suggestions).

### Saving (`savegame.py`)

`run_story()` writes a checkpoint at the start of every scene. A save is a small JSON file named after the character
(`saves/<name>.json`) that stores *which story, which scene, and the character's name, class and level*:

```json
{
  "version": 1,
  "saved_at": "2026-10-29 14:03",
  "story": "Mageborne: The Emberpine Woods",
  "scene": "chapter2",
  "completed": false,
  "player": { "name": "Tester", "class": "Mage", "level": 2 }
}
```

Because only the scene's name is stored, stats always come from the current class and monster definitions, so balance changes apply
to old saves. Files are written to a temporary file first and then swapped in, so a crash mid-save can't corrupt an existing save.
If the saves folder can't be written to, the game warns once and carries on without saving.

---

## Modding

A mod is a folder in `mods/`. Everything inside is optional:

```
mods/my_mod/
  mod.json         name, author, version (display only)
  monsters.json    new monsters, with stats and abilities
  classes.json     new character classes
  story.json       a storyline (or several in a "stories" folder)
  anything.py      custom monsters, classes and abilities written in Python
```

For example, a monster with a stunning gaze needs no code:

```json
{
  "medusa": {
    "emoji": "🐍", "hp": 16, "attack": 4, "atk_min": 2, "atk_max": 3,
    "abilities": [ { "type": "stun", "turns": 2, "range": 4, "cooldown": 5 } ]
  }
}
```

Highlights of the mod system:

- **Easy to start:** rename `mods/_example_mod` to `example_mod` to see a working class, monsters, a custom ability and a story.
- **Safe by default:** JSON mods can't run code. A broken mod never crashes the game; it's skipped and explained at startup.
- **Switch off a mod** by putting an underscore at the start of its folder name.
- **Override built-ins:** a mod monster/class/ability with the same name as a built-in replaces it (later mods win).
- **Python mods run real code**, so only install ones you trust.

The complete reference, covering every field, the ability settings, the `game` toolbox and story format, is in **[`mods/README.md`](mods/README.md)**.

### Generating a mod template

You don't have to write the starter files by hand. Either way creates a working mod folder in `mods/` that already loads and plays:

- **In the game:** main menu → **Create a mod template**. It asks for a name, an optional author, and which parts to include
  (monsters, classes, story, a Python file). Press Enter for the first three.
- **From a terminal:**

  ```
  python main.py --new-mod "Frost Pack" --author "Your Name" --only monsters,classes,story,python
  ```

  `--author` and `--only` are optional. `--only` takes any of `monsters`, `classes`, `story`, `python`
  (default: `monsters,classes,story`).

The generated folder (named after your mod, e.g. `mods/frost_pack/`) contains `mod.json`, plus whichever of `monsters.json`,
`classes.json`, `story.json` and `<name>.py` you chose, and a short `README.md`. The starter content is named after your mod so it never clashes with
built-ins: a monster with a stun ability, a character class, and a tiny story that uses your monster. Edit, restart the game, and
it's there. It refuses to overwrite an existing mod folder.

---

## Configuration

Game-wide settings live in `config.py`:

| Setting | Default | Meaning |
|---|---|---|
| `GRID_SIZE` | `6` | battle grid is `GRID_SIZE × GRID_SIZE` |
| `FLOOR` | `🟫` | empty tile emoji |
| `REST_HEAL` | `3` | Rest always heals at least this much |
| `REST_HEAL_PCT` | `0.2` | …or this fraction of max HP, whichever is more |
| `MODS_DIR`, `STORIES_DIR` | `mods/`, `stories/` | where content is loaded from |
| `SAVES_DIR` | `saves/` | where save files are written |

Class and monster numbers are in their own files (`player_classes/*.py`, `monsters/*.py`).

---

## Balance notes

The built-in fights were tuned with a headless simulator (not included in the project) that played every fight as every class with
three kinds of player: one that just trades blows, one that dodges and rests sensibly, and one with perfect lookahead. The aim:

- Trading blows works for the early fights but is risky, and loses to the troll.
- Using **Rest**, **Guard**, target choice and dodging makes the difference, especially against the fairies and the troll.
- No class should be hopeless in any fight.

Things that shape the balance: melee being orthogonal-only, the Thief's extra speed, health coming from constitution, Rest being a fixed
fraction of max HP, and the troll being as fast as the player.

If you change numbers, test each fight as a few different classes, and watch out for **infinite-heal stalemates** (if Rest heals more than a monster deals,
a fight can stall) and **free kiting** (if you're much faster than a melee monster, you can hit-and-run without risk).

---

## Troubleshooting

| Problem | Fix |
|---|---|
| **The grid looks misaligned or an emoji overlaps its neighbor** | Some emoji are drawn at the wrong width by some terminals/fonts. Built-in emoji are all plain single characters to avoid this. For mods, use a single-character emoji; skin tones, ❤️-style emoji and combined emoji are the usual culprits (the loader warns about them). |
| **`ModuleNotFoundError`** | Run `main.py` from inside the `mageborne` folder, or run it directly by path. The files import each other by name. |
| **A mod doesn't show up** | Check the folder is directly inside `mods/`, its name doesn't start with `_` or `.`, and its files are directly inside it (not in a sub-folder). Read the `⚠` messages at startup. |
| **A monster never moves** | It's idle: you're outside its chase radius. Look for the 💤 line under the grid. |
| **The screen doesn't clear** | The game uses `cls` on Windows and `clear` elsewhere; make sure it runs in a real console window. |
| **Continue says a save can't be used** | The message says what's missing: usually a mod (story or class) that isn't installed any more, or a story whose scenes were renamed. Put the mod back, or start a new game. |
| **"Couldn't save your progress"** | The `saves/` folder can't be written to (read-only location, or a file named `saves` is in the way). Move the game to a normal folder. The game keeps working, just without saving. |
| **Story won't load** | The startup report tells you the scene and field that's wrong, e.g. `goes to scene "fihgt", but no scene has that name (did you mean "fight"?)`. |

---

## Extending the base game

You don't have to use the mod system to add content to the game itself:

- **A new monster:** create a file in `monsters/` with a `Monster` subclass, then add it to `MONSTER_TYPES` in `monsters/registry.py`.
- **A new class:** create a file in `player_classes/` with a `Player` subclass, then add it to `PLAYER_CLASSES` in `player_classes/__init__.py`.
- **A new ability:** subclass `Ability` in `abilities.py` and add it to the registration loop at the bottom of the file.
- **A new story:** drop a JSON file in `stories/`. It appears in the adventure menu automatically.

Anything that works as a mod works the same way when built in, so the easiest way to develop content is as a mod first.
