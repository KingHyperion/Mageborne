"""Creates a ready-to-edit mod folder in mods/ (monsters.json, classes.json, story.json, ...).

Three ways to use it:
  - in the game's main menu: "Create a mod template"
  - from a terminal:  python main.py --new-mod "My Mod" [--author "You"] [--only monsters,story]
  - from your own code: create_mod("My Mod")
"""
import os
import re

from config import MODS_DIR
from savegame import slugify

KINDS    = ("monsters", "classes", "story", "python")
DEFAULT  = ("monsters", "classes", "story")


class TemplateError(Exception):
    """Something the player can fix (bad name, folder already exists...)."""


MOD_JSON = """{
  "name": "__TITLE__",
  "author": "__AUTHOR__",
  "version": "0.1",
  "description": "Describe your mod here."
}
"""

MONSTERS_JSON = """{
  "__SLUG___monster": {
    "emoji": "🐺",
    "hp": 12,
    "attack": 3,
    "chase_radius": 5,
    "atk_min": 1,
    "atk_max": 1,
    "speed": 1,
    "abilities": [
      { "type": "stun", "turns": 1, "range": 3, "cooldown": 6 }
    ]
  }
}
"""

CLASSES_JSON = """{
  "__TITLE__ Hero": {
    "description": "A hero from __TITLE__. Edit me!",
    "emoji": "🦸",
    "strength": 12,
    "dexterity": 12,
    "constitution": 14,
    "intelligence": 12,
    "attack": 6,
    "atk_range": 2,
    "speed": 2
  }
}
"""

STORY_JSON = """{
  "title": "__TITLE__ Adventure",
  "author": "__AUTHOR__",
  "description": "A tiny starter story. Edit me!",
  "start": "start",
  "scenes": {

    "start": {
      "text": [
        "Welcome, {name} the {class}!",
        "Something is stirring in the dark ahead..."
      ],
      "next": "choice"
    },

    "choice": {
      "text": "What do you do?",
      "choices": [
        {
          "text": "Charge in",
          "goto": "fight"
        },
        {
          "text": "Sneak up on it",
          "goto": "fight",
          "check": { "stat": "dexterity", "dc": 12, "label": "stealth",
                     "fail_text": "A twig snaps under your foot. Try something else!" }
        }
      ]
    },

    "fight": {
      "text": "Two monsters leap out at you!",
      "encounter": { "__MONSTER__": 2 },
      "level_up": true,
      "next": "ending"
    },

    "ending": {
      "text": [
        "The path is clear at last.",
        "",
        "THE END"
      ],
      "end": true
    }
  }
}
"""

PYTHON_PY = '''# Custom monsters, classes and abilities for "__TITLE__".
# The game finds every Monster, Player and Ability subclass in this file automatically.
# (Files that start with an underscore are ignored.)
from modding import Monster, Player, Ability, Stun, Breath, Slam, Heal


class __PASCAL__Beast(Monster):
    name         = "__SLUG___beast"     # the name stories use in "encounter"
    emoji        = "🦂"
    max_hp       = 14
    attack       = 3
    chase_radius = 5
    atk_min      = 1
    atk_max      = 1
    abilities    = [Heal(amount=3, below=0.5, cooldown=3)]

    # For completely custom behavior, override take_turn:
    #
    # def take_turn(self, game):
    #     game.say(f"{self.emoji} The beast snarls!")
    #     super().take_turn(game)


# A custom character class would look like this:
#
# class __PASCAL__Ranger(Player):
#     class_name  = "__TITLE__ Ranger"
#     description = "A sharp-eyed archer."
#     emoji       = "🏹"
#     strength, dexterity, constitution, intelligence = 10, 15, 12, 12
#     attack      = 5
#     atk_range   = 4
#     speed       = 2


# A brand-new ability. Once defined, monsters.json can use it as {"type": "zap"}:
#
# class Zap(Ability):
#     ability_type = "zap"
#     PARAMS   = {**Ability.PARAMS, "damage": int}    # settings JSON may give it
#     damage   = 4
#     range    = 3
#     cooldown = 3
#
#     def use(self, monster, game):
#         dealt = game.damage_player(self.damage)
#         self.say(game, monster, "{emoji} {name} zaps you for {damage}!", damage=dealt)
#         self.start_cooldown()
#         return True        # True = this used up the monster's turn
'''

NOTES_MD = """# __TITLE__

Your new mod. The game loads this folder automatically, so start the game to see it.

| file | what it is |
|---|---|
__FILE_ROWS__
Tips:

- Rename this folder to start with `_` to switch the mod off.
- If the game shows a ⚠ message at startup, it tells you which file and line to fix.
- The full guide is in `mods/README.md`.
"""

FILE_ROWS = {
    "mod.json":      "| `mod.json` | name, author and version (display only) |\n",
    "monsters.json": "| `monsters.json` | a starter monster with a stun ability |\n",
    "classes.json":  "| `classes.json` | a starter character class |\n",
    "story.json":    "| `story.json` | a tiny story that uses your monster |\n",
    "__PY__":        "| `__SLUG__.py` | custom monsters, classes and abilities in Python |\n",
}


def _pascal(slug):
    pascal = "".join(part.capitalize() for part in slug.split("_") if part)
    return pascal if pascal and not pascal[0].isdigit() else "Mod" + pascal


def create_mod(name, kinds=DEFAULT, author="Your Name", mods_dir=None):
    """Write a new mod folder. Returns (folder_path, [file names]). Raises TemplateError."""
    mods_dir = mods_dir or MODS_DIR
    name = str(name).strip()
    slug = slugify(name, fallback="")
    if not slug:
        raise TemplateError("Please give your mod a name using letters or numbers, e.g. \"Frost Pack\".")
    unknown = [k for k in kinds if k not in KINDS]
    if unknown:
        raise TemplateError(f'Unknown part "{unknown[0]}". Choose from: {", ".join(KINDS)}.')
    kinds = [k for k in KINDS if k in kinds] or list(DEFAULT)

    folder = os.path.join(mods_dir, slug)
    if os.path.exists(folder):
        raise TemplateError(f'There is already a mod folder called "{slug}". Pick another name.')

    title  = re.sub(r"\s+", " ", name) if re.search(r"[A-Za-z0-9]", name) else slug
    author = str(author).strip() or "Your Name"
    pascal = _pascal(slug)
    if "monsters" in kinds:
        monster = f"{slug}_monster"
    elif "python" in kinds:
        monster = f"{slug}_beast"
    else:
        monster = "goblin"

    def fill(text):
        return (text.replace("__TITLE__", title).replace("__AUTHOR__", author)
                    .replace("__SLUG__", slug).replace("__PASCAL__", pascal)
                    .replace("__MONSTER__", monster))

    files = {"mod.json": fill(MOD_JSON)}
    if "monsters" in kinds: files["monsters.json"] = fill(MONSTERS_JSON)
    if "classes" in kinds:  files["classes.json"]  = fill(CLASSES_JSON)
    if "story" in kinds:    files["story.json"]    = fill(STORY_JSON)
    if "python" in kinds:   files[f"{slug}.py"]    = fill(PYTHON_PY)
    rows = "".join(fill(FILE_ROWS[k]) for k in ("mod.json", "monsters.json", "classes.json", "story.json")
                   if k in files)
    if f"{slug}.py" in files:
        rows += fill(FILE_ROWS["__PY__"])
    files["README.md"] = fill(NOTES_MD).replace("__FILE_ROWS__\n", rows + "\n")

    os.makedirs(folder)
    for fname, content in files.items():
        with open(os.path.join(folder, fname), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    return folder, list(files)
