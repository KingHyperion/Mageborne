import sys

sys.dont_write_bytecode = True      # keep __pycache__ folders out of the project and mods

import argparse

import savegame
from mod_loader import load_content
from mod_template import DEFAULT, KINDS, TemplateError, create_mod
from player_classes import PLAYER_CLASSES
from story import STORIES, run_story
from ui import menu_keys, prompt_choice


# ── Startup report ────────────────────────────────────────────
def show_load_report(report):
    if not report.lines:
        return                      # no mods installed - say nothing
    print("Mods:")
    print("\n".join(report.lines))
    if report.has_problems:
        input("\n  [Some mod content was skipped - press Enter to continue]")
    print()


# ── Menus ─────────────────────────────────────────────────────
def main_menu(save_count):
    options = [("new", "New game")]
    if save_count:
        options.append(("continue", f"Continue ({save_count} save{'' if save_count == 1 else 's'})"))
    options += [("mod", "Create a mod template"), ("quit", "Quit")]
    keys = menu_keys(len(options))
    prompt = "Welcome to Mageborne!\n" + "".join(
        f"  {k}) {label}\n" for k, (_, label) in zip(keys, options))
    return options[keys.index(prompt_choice(prompt, keys))][0]


def choose_story():
    stories = list(STORIES.values())
    if len(stories) == 1:
        return stories[0]           # only the built-in story - no menu needed
    keys = menu_keys(len(stories))
    lines = []
    for key, s in zip(keys, stories):
        extra = " - " + s["description"] if s.get("description") else ""
        by    = f" (by {s['author']})" if s.get("author") else ""
        lines.append(f"  {key}) {s['title']}{by}{extra}\n")
    return stories[keys.index(prompt_choice("Choose your adventure:\n" + "".join(lines), keys))]


def choose_class():
    classes = list(PLAYER_CLASSES.values())
    keys    = menu_keys(len(classes))
    prompt  = "Please choose one of the classes below:\n" + "".join(
        f"  {k}) {c.class_name}: {c.description}\n" for k, c in zip(keys, classes)
    )
    return classes[keys.index(prompt_choice(prompt, keys))]


# ── New game ──────────────────────────────────────────────────
def new_game():
    story = choose_story()
    cls   = choose_class()
    print(f"\nYou have selected: {cls.class_name}")
    while True:
        name = input("Please enter a name for your character: ")
        if not savegame.save_exists(name):
            break
        answer = prompt_choice(
            f'\nA save for "{name}" already exists. Starting a new game with this name will replace it.\n'
            "  A) Replace it\n  B) Pick another name\n", ["A", "B"])
        if answer == "A":
            break
    player = cls(name)
    player.describe()
    input("\n  [Press Enter to begin your adventure]")
    return run_story(story, player)


# ── Continue ──────────────────────────────────────────────────
def continue_game():
    """Returns True if a game was played, False to go back to the main menu."""
    saves = savegame.list_saves()
    keys  = menu_keys(len(saves) + 1)
    lines = []
    for key, s in zip(keys, saves):
        if "error" in s:
            lines.append(f"  {key}) ⚠ {s['error']}\n")
            continue
        done = "  [finished]" if s["completed"] else ""
        lines.append(f"  {key}) {s['name']} - {s['class']}, level {s['level']} - "
                     f"{s['story']} (saved {s['saved_at']}){done}\n")
    lines.append(f"  {keys[len(saves)]}) Back\n")
    pick = keys.index(prompt_choice("Choose a save to continue:\n" + "".join(lines), keys))
    if pick == len(saves):
        return False
    info = saves[pick]
    try:
        if "error" in info:
            raise savegame.SaveError(info["error"])
        if info["completed"]:
            raise savegame.SaveError("That adventure is already finished! Start a new game to play it again.")
        story, player, scene = savegame.resolve_save(info, STORIES, PLAYER_CLASSES)
    except savegame.SaveError as e:
        print(f"\n  {e}")
        input("\n  [Press Enter to go back]")
        return False
    run_story(story, player, start_scene=scene)
    return True


# ── Mod template maker ────────────────────────────────────────
def make_mod_template():
    print("\nCreate a mod template - a folder with example files you can edit.")
    name   = input("Name for your mod (for example: Frost Pack): ")
    author = input("Your name (optional): ")
    print("\nWhat should it include? Type the letters, or just press Enter for A, B and C.")
    labels = {"monsters": "monsters.json - new monsters",
              "classes":  "classes.json - new character classes",
              "story":    "story.json - a storyline",
              "python":   "a Python file - custom code (advanced)"}
    letters = "ABCD"
    for letter, kind in zip(letters, KINDS):
        print(f"  {letter}) {labels[kind]}")
    chosen = input("> ").upper()
    kinds = [kind for letter, kind in zip(letters, KINDS) if letter in chosen] or list(DEFAULT)
    try:
        folder, files = create_mod(name, kinds, author or "Your Name")
    except TemplateError as e:
        print(f"\n  {e}")
        input("\n  [Press Enter to go back]")
        return
    print(f"\n  ✔ Created {folder}")
    print("    " + ", ".join(files))
    print("\n  Edit those files, then start the game again to see your mod.")
    input("\n  [Press Enter to go back]")


# ── Entry point ───────────────────────────────────────────────
def parse_args(argv):
    p = argparse.ArgumentParser(description="Mageborne - a turn-based text RPG.")
    p.add_argument("--new-mod", metavar="NAME", help="create a mod template folder in mods/ and exit")
    p.add_argument("--author", default="Your Name", help="author name for --new-mod")
    p.add_argument("--only", metavar="PARTS", default=",".join(DEFAULT),
                   help=f"comma-separated parts for --new-mod: {', '.join(KINDS)} "
                        f"(default: {','.join(DEFAULT)})")
    return p.parse_args(argv)


def cli_new_mod(args):
    kinds = [k.strip().lower() for k in args.only.split(",") if k.strip()]
    try:
        folder, files = create_mod(args.new_mod, kinds, args.author)
    except TemplateError as e:
        print(e)
        return 1
    print(f"Created {folder}")
    for f in files:
        print(f"  {f}")
    print("Edit those files, then run the game to see your mod.")
    return 0


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.new_mod is not None:
        return cli_new_mod(args)

    report = load_content()
    show_load_report(report)
    if not STORIES:
        print("No playable story was found - check the messages above.")
        input("\n  [Press Enter to exit]")
        return 1

    while True:
        action = main_menu(len(savegame.list_saves()))
        if action == "quit":
            return 0
        if action == "mod":
            make_mod_template()
        elif action == "continue":
            if continue_game():
                return 0
        else:
            new_game()
            return 0


if __name__ == "__main__":
    sys.exit(main())
