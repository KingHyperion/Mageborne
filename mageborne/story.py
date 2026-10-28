"""Story engine: reads story JSON files, checks them for mistakes, and plays them.

A story is a set of named scenes. Each scene shows some text, can start a fight,
and then moves on (a choice menu, a "next" scene, or the end). See mods/README.md.
"""
import json
import random
from difflib import get_close_matches

from game import start_encounter
from monsters import MONSTER_TYPES
from monsters.spawner import spawn_capacity
from ui import clear_screen, menu_keys, prompt_choice

STORIES = {}   # story title -> story dict

STATS        = ("strength", "dexterity", "constitution", "intelligence")
STORY_KEYS   = {"title", "author", "description", "start", "scenes"}
SCENE_KEYS   = {"text", "choices", "next", "end", "encounter", "level_up",
                "fight_prompt", "continue_prompt"}
CHOICE_KEYS  = {"text", "goto", "check"}
CHECK_KEYS   = {"stat", "dc", "label", "fail_text", "retry_prompt", "fail_goto"}


# ── Loading ───────────────────────────────────────────────────
def load_story_file(path, label, source=None):
    """Read one story file into STORIES. Raises on bad JSON. Returns the title."""
    with open(path, encoding="utf-8") as f:
        story = json.load(f)
    if not isinstance(story, dict):
        raise ValueError('a story file must start with { and contain "scenes"')
    stem = path.replace("\\", "/").rsplit("/", 1)[-1].rsplit(".", 1)[0]
    title = str(story.get("title") or stem.replace("_", " ").title())
    story["title"]  = title
    story["_label"] = label
    story["_source"] = source
    STORIES[title] = story
    return title


# ── Checking ──────────────────────────────────────────────────
def _lines(value):
    if value is None:
        return []
    return value.split("\n") if isinstance(value, str) else list(value)


def _suggest(word, options):
    match = get_close_matches(str(word), list(options), n=1)
    return f' (did you mean "{match[0]}"?)' if match else ""


def _unknown_keys(obj, allowed, where, errors):
    for key in obj:
        if key not in allowed:
            errors.append(f'{where}: unknown field "{key}"{_suggest(key, allowed)}')


def _is_text(value):
    return isinstance(value, str) or (
        isinstance(value, list) and all(isinstance(v, str) for v in value))


def validate_story(story):
    """Return a list of plain-English problems (empty list = story is fine)."""
    errors = []
    scenes = story.get("scenes")
    if not isinstance(scenes, dict) or not scenes:
        return ['"scenes" is missing or empty - a story needs at least one scene']
    _unknown_keys({k: v for k, v in story.items() if not k.startswith("_")},
                  STORY_KEYS, "story", errors)

    def check_ref(target, where):
        if not isinstance(target, str) or target not in scenes:
            errors.append(f'{where}: goes to scene "{target}", but no scene has that name'
                          f'{_suggest(target, scenes)}')

    start = story.get("start", "start")
    if start not in scenes:
        errors.append(f'the first scene "{start}" doesn\'t exist - add a scene named '
                      f'"{start}" or set "start" to one of your scenes')

    capacity = spawn_capacity()
    for sid, sc in scenes.items():
        where = f'scene "{sid}"'
        if not isinstance(sc, dict):
            errors.append(f"{where} must be an object like {{ \"text\": ... }}")
            continue
        _unknown_keys(sc, SCENE_KEYS, where, errors)
        if "text" in sc and not _is_text(sc["text"]):
            errors.append(f'{where}: "text" must be a string or a list of strings')

        exits = [k for k in ("choices", "next", "end") if sc.get(k)]
        if not exits:
            errors.append(f'{where} has no "choices", "next" or "end" - '
                          f'the story would get stuck here')
        elif len(exits) > 1:
            errors.append(f'{where} uses more than one of "choices", "next", "end" - pick one')
        if sc.get("choices") and (sc.get("encounter") or sc.get("level_up")):
            errors.append(f'{where}: a scene with "choices" can\'t also have "encounter" or '
                          f'"level_up" - put those in the scene the choice leads to')

        if "next" in sc:
            check_ref(sc["next"], where + ' "next"')

        enc = sc.get("encounter")
        if enc is not None:
            if not isinstance(enc, dict) or not enc:
                errors.append(f'{where}: "encounter" must look like {{"goblin": 3}}')
            else:
                for mname, count in enc.items():
                    if str(mname).lower() not in MONSTER_TYPES:
                        errors.append(f'{where}: unknown monster "{mname}"'
                                      f'{_suggest(mname, MONSTER_TYPES)}. '
                                      f'Available: {", ".join(MONSTER_TYPES)}')
                    if isinstance(count, bool) or not isinstance(count, int) or count < 1:
                        errors.append(f'{where}: monster count for "{mname}" must be a whole number, 1 or more')
                if all(isinstance(c, int) and not isinstance(c, bool) for c in enc.values()) \
                        and sum(enc.values()) > capacity:
                    errors.append(f'{where}: {sum(enc.values())} monsters won\'t fit on the grid '
                                  f'(max {capacity})')

        choices = sc.get("choices")
        if choices is not None:
            if not isinstance(choices, list) or not choices:
                errors.append(f'{where}: "choices" must be a list of {{"text": ..., "goto": ...}}')
                continue
            for i, ch in enumerate(choices, 1):
                cw = f'{where}, choice {i}'
                if not isinstance(ch, dict):
                    errors.append(f'{cw} must be an object like {{"text": "...", "goto": "..."}}')
                    continue
                _unknown_keys(ch, CHOICE_KEYS, cw, errors)
                if not isinstance(ch.get("text"), str):
                    errors.append(f'{cw}: needs "text" (what the player sees)')
                check_ref(ch.get("goto"), cw + ' "goto"')
                chk = ch.get("check")
                if chk is not None:
                    if not isinstance(chk, dict):
                        errors.append(f'{cw}: "check" must be an object')
                        continue
                    _unknown_keys(chk, CHECK_KEYS, cw + ' check', errors)
                    if chk.get("stat") not in STATS:
                        errors.append(f'{cw} check: "stat" must be one of {", ".join(STATS)}')
                    if isinstance(chk.get("dc"), bool) or not isinstance(chk.get("dc"), (int, float)):
                        errors.append(f'{cw} check: "dc" (the number to beat) must be a number')
                    if "fail_goto" in chk:
                        check_ref(chk["fail_goto"], cw + ' check "fail_goto"')
    return errors


# ── Playing ───────────────────────────────────────────────────
def _fill(text, player):
    return (text.replace("{name}", player.name)
                .replace("{class}", player.class_name)
                .replace("{level}", str(player.level)))


def _say(text, player):
    if not text:
        return
    print()
    for line in _lines(text):
        line = _fill(line, player)
        print("  " + line if line else "")


def _ask_choice(scene, player):
    choices = scene["choices"]
    keys    = menu_keys(len(choices))
    header  = "\n".join(_fill(l, player) for l in _lines(scene.get("text")))
    options = "".join(f"  {k}) {_fill(c['text'], player)}\n" for k, c in zip(keys, choices))
    while True:
        clear_screen()
        pick = choices[keys.index(prompt_choice(f"\n{header}\n{options}", keys))]
        check = pick.get("check")
        if not check:
            return pick["goto"]
        stat = check["stat"]
        roll = random.randint(1, 20) + getattr(player, stat) / 10
        print(f"\n  You rolled a {roll:.1f} total for {check.get('label', stat)}.")
        if roll >= check["dc"]:
            return pick["goto"]
        print("  " + _fill(check.get("fail_text", "That didn't work - try another approach."), player))
        if check.get("fail_goto"):
            input("\n  [Press Enter to continue]")
            return check["fail_goto"]
        input(f"\n  [{check.get('retry_prompt', 'Press Enter to try another tactic')}]")


def _play_scene(scene, player, via_choice):
    """Play one scene. Returns (next_scene_id or None, reached_via_choice)."""
    if scene.get("choices"):
        return _ask_choice(scene, player), True

    if not via_choice:
        clear_screen()
    _say(scene.get("text"), player)

    if scene.get("encounter"):
        input(f"\n  [{scene.get('fight_prompt', 'Press Enter to start combat')}]")
        start_encounter(scene["encounter"], player)
    if scene.get("level_up"):
        player.level_up()
        clear_screen()
        print(f"\n  🎉 Congratulations! You're now level {player.level}.\n")
        input(f"  [{scene.get('continue_prompt', 'Press Enter to continue')}]")
    elif scene.get("end") or (scene.get("next") and not scene.get("encounter")):
        default = "Press Enter to exit" if scene.get("end") else "Press Enter to continue"
        input(f"\n  [{scene.get('continue_prompt', default)}]")
    return scene.get("next"), False


def run_story(story, player):
    scenes   = story["scenes"]
    scene_id = story.get("start", "start")
    via_choice = False
    while scene_id is not None:
        scene_id, via_choice = _play_scene(scenes[scene_id], player, via_choice)
