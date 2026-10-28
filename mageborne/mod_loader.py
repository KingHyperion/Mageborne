"""Finds mods in the mods/ folder and loads their monsters, classes and stories.

Nothing in here needs editing to add content - see mods/README.md.
A broken mod never crashes the game: it is skipped and explained in the startup report.
"""
import importlib.util
import json
import os
import re
import sys
import unicodedata
from difflib import get_close_matches

import story as story_engine
from abilities import ABILITY_TYPES, Ability
from config import MODS_DIR, STORIES_DIR
from monsters import Monster, MONSTER_TYPES
from player import Player
from player_classes import PLAYER_CLASSES

NUMBER = (int, float)
MONSTER_FIELDS = {"emoji": str, "hp": int, "attack": int, "chase_radius": NUMBER,
                  "atk_min": NUMBER, "atk_max": NUMBER, "speed": int, "abilities": list}
CLASS_FIELDS   = {"description": str, "emoji": str, "strength": int, "dexterity": int,
                  "constitution": int, "intelligence": int, "attack": int, "atk_range": NUMBER,
                  "speed": int}


class LoadReport:
    def __init__(self):
        self.lines = []
        self.has_problems = False
        self.problem_count = 0

    def ok(self, text):      self.lines.append(f"  ✔ {text}")
    def info(self, text):    self.lines.append(f"  • {text}")
    def detail(self, text):  self.lines.append(f"      - {text}")
    def problem(self, text):
        self.lines.append(f"  ⚠ {text}")
        self.has_problems = True
        self.problem_count += 1


# ── Small helpers ─────────────────────────────────────────────
def _describe_error(e):
    if isinstance(e, json.JSONDecodeError):
        return f"line {e.lineno}, column {e.colno}: {e.msg} (look for a missing comma or quote)"
    if isinstance(e, SyntaxError):
        return f"line {e.lineno}: {e.msg}"
    return f"{type(e).__name__}: {e}"


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _plural(n, word):
    return f"{n} {word}{'' if n == 1 else ('es' if word.endswith('s') else 's')}"


def _check_entry(entry, fields, where):
    """Return a list of problems with one JSON monster/class entry."""
    if not isinstance(entry, dict):
        return [f'{where}: must be an object like {{"emoji": "..."}}']
    problems = []
    for key, value in entry.items():
        if key not in fields:
            match = get_close_matches(key, list(fields), n=1)
            hint = f' (did you mean "{match[0]}"?)' if match else ""
            problems.append(f'{where}: unknown field "{key}"{hint}. Allowed: {", ".join(fields)}')
        elif isinstance(value, bool) or not isinstance(value, fields[key]):
            kind = "text" if fields[key] is str else "a number"
            problems.append(f'{where}: "{key}" must be {kind}, not {value!r}')
    return problems


def _check_emoji(emoji, what, mod, report):
    """Warn (but still load) if an emoji is likely to draw misaligned in a terminal."""
    if not isinstance(emoji, str):
        return
    if len(emoji) != 1 or unicodedata.east_asian_width(emoji) != "W":
        report.problem(f'{mod}: {what}: emoji "{emoji}" may draw misaligned on the grid. '
                       f'Use a plain single-character emoji (no skin tones, no combined emoji)')


def _build_abilities(specs, where, mod, report):
    """Turn a JSON "abilities" list into Ability objects. Returns None if anything is wrong."""
    abilities, ok = [], True
    for i, spec in enumerate(specs, 1):
        w = f"{where} ability {i}"
        if not isinstance(spec, dict) or "type" not in spec:
            report.problem(f'{mod}: {w}: must look like {{"type": "stun", ...}}')
            ok = False
            continue
        kind = str(spec["type"]).lower()
        cls  = ABILITY_TYPES.get(kind)
        if cls is None:
            match = get_close_matches(kind, list(ABILITY_TYPES), n=1)
            hint  = f' (did you mean "{match[0]}"?)' if match else ""
            report.problem(f'{mod}: {w}: unknown ability type "{kind}"{hint}. '
                           f'Available: {", ".join(ABILITY_TYPES)}')
            ok = False
            continue
        settings = {k: v for k, v in spec.items() if k != "type"}
        problems = _check_entry(settings, cls.PARAMS, w)
        if problems:
            for p in problems:
                report.problem(f"{mod}: {p}")
            ok = False
            continue
        abilities.append(cls(**settings))
    return abilities if ok else None


def _class_ident(text, fallback):
    return re.sub(r"\W", "", text.title()) or fallback


# ── Registering content ───────────────────────────────────────
def _add_monster(key, cls, mod, counts, report):
    key = key.strip().lower()
    if key in MONSTER_TYPES:
        report.info(f'{mod} replaced the existing monster "{key}"')
    MONSTER_TYPES[key] = cls
    counts["monsters"] += 1


def _add_ability(name, cls, mod, counts, report):
    name = name.strip().lower()
    if name in ABILITY_TYPES:
        report.info(f'{mod} replaced the existing ability "{name}"')
    ABILITY_TYPES[name] = cls
    counts["abilities"] += 1


def _add_class(name, cls, mod, counts, report):
    if name in PLAYER_CLASSES:
        report.info(f'{mod} replaced the existing class "{name}"')
    PLAYER_CLASSES[name] = cls
    counts["classes"] += 1


# ── Loaders for each kind of mod file ─────────────────────────
def _load_monsters_json(path, mod, counts, report):
    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError('monsters.json must look like {"slime": {"emoji": "🟢", ...}}')
    for name, entry in data.items():
        where = f'monsters.json "{name}"'
        problems = _check_entry(entry, MONSTER_FIELDS, where)
        if not problems:
            lo = entry.get("atk_min", Monster.atk_min)
            hi = entry.get("atk_max", Monster.atk_max)
            if lo > hi:
                problems.append(f'{where}: "atk_min" ({lo}) is bigger than "atk_max" ({hi})')
            if entry.get("hp", 1) < 1:
                problems.append(f'{where}: "hp" must be at least 1')
        if problems:
            for p in problems:
                report.problem(f"{mod}: {p}")
            continue
        _check_emoji(entry.get("emoji", Monster.emoji), f'monster "{name}"', mod, report)
        attrs = {("max_hp" if k == "hp" else k): v for k, v in entry.items() if k != "abilities"}
        if "abilities" in entry:
            built = _build_abilities(entry["abilities"], where, mod, report)
            if built is None:
                continue
            attrs["abilities"] = built
        attrs.update(name=name.strip().lower(), __module__=f"mods.{mod}")
        cls = type(_class_ident(name, "ModMonster"), (Monster,), attrs)
        _add_monster(name, cls, mod, counts, report)


def _load_classes_json(path, mod, counts, report):
    data = _read_json(path)
    if not isinstance(data, dict):
        raise ValueError('classes.json must look like {"Paladin": {"emoji": "🦸", ...}}')
    for name, entry in data.items():
        problems = _check_entry(entry, CLASS_FIELDS, f'classes.json "{name}"')
        if problems:
            for p in problems:
                report.problem(f"{mod}: {p}")
            continue
        _check_emoji(entry.get("emoji", Player.emoji), f'class "{name}"', mod, report)
        attrs = dict(entry, class_name=name, __module__=f"mods.{mod}")
        cls = type(_class_ident(name, "ModClass"), (Player,), attrs)
        _add_class(name, cls, mod, counts, report)


def _load_python(path, mod, counts, report):
    stem   = os.path.splitext(os.path.basename(path))[0]
    mod_id = "mageborne_mod_" + re.sub(r"\W", "_", f"{mod}_{stem}")
    spec   = importlib.util.spec_from_file_location(mod_id, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_id] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        del sys.modules[mod_id]
        raise
    found = False
    for obj in list(vars(module).values()):
        if not isinstance(obj, type) or obj.__module__ != mod_id:
            continue   # skip imported things like Monster itself
        if issubclass(obj, Monster):
            _check_emoji(obj.emoji, f"monster {obj.__name__}", mod, report)
            _add_monster(obj.__dict__.get("name") or obj.__name__, obj, mod, counts, report)
            found = True
        elif issubclass(obj, Ability):
            _add_ability(obj.__dict__.get("ability_type") or obj.__name__, obj, mod, counts, report)
            found = True
        elif issubclass(obj, Player):
            _check_emoji(obj.emoji, f"class {obj.__name__}", mod, report)
            _add_class(obj.__dict__.get("class_name") or obj.__name__, obj, mod, counts, report)
            found = True
    if not found:
        report.info(f"{mod}/{os.path.basename(path)}: no Monster, Player or Ability subclasses found (skipped)")


def _load_story(path, mod_folder, mod_title, counts, report):
    label = os.path.relpath(path, MODS_DIR).replace("\\", "/")
    story_engine.load_story_file(path, label, source=mod_title)
    counts["stories"] += 1


# ── One mod folder ────────────────────────────────────────────
def _load_one_mod(folder, report):
    folder_name = os.path.basename(folder)
    meta = {}
    meta_path = os.path.join(folder, "mod.json")
    if os.path.isfile(meta_path):
        try:
            meta = _read_json(meta_path)
            if not isinstance(meta, dict):
                raise ValueError("mod.json must be an object like {\"name\": \"My Mod\"}")
        except Exception as e:
            report.problem(f"{folder_name}/mod.json: {_describe_error(e)}")
            meta = {}
    problems_before = report.problem_count
    title  = str(meta.get("name", folder_name))
    counts = {"monsters": 0, "classes": 0, "abilities": 0, "stories": 0}

    jobs = []   # (file name, function that loads it) - Python first, so JSON can use what it defines
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(".py") and not f.startswith("_"):
            path = os.path.join(folder, f)
            jobs.append((f, lambda p=path: _load_python(p, title, counts, report)))
    for fname, fn in (("monsters.json", _load_monsters_json), ("classes.json", _load_classes_json)):
        path = os.path.join(folder, fname)
        if os.path.isfile(path):
            jobs.append((fname, lambda p=path, f=fn: f(p, title, counts, report)))
    story_files = []
    if os.path.isfile(os.path.join(folder, "story.json")):
        story_files.append(os.path.join(folder, "story.json"))
    stories_dir = os.path.join(folder, "stories")
    if os.path.isdir(stories_dir):
        story_files += [os.path.join(stories_dir, f) for f in sorted(os.listdir(stories_dir))
                        if f.lower().endswith(".json")]
    for path in story_files:
        jobs.append((os.path.relpath(path, folder).replace("\\", "/"),
                     lambda p=path: _load_story(p, folder, title, counts, report)))

    for rel, job in jobs:
        try:
            job()
        except Exception as e:
            report.problem(f"{folder_name}/{rel}: {_describe_error(e)}")

    if not jobs:
        report.problem(f'{folder_name}: nothing to load. Put monsters.json, classes.json, story.json '
                       f'or .py files directly inside this folder (not in another folder inside it).')
        return
    parts = [_plural(n, w) for w, n in (("monster", counts["monsters"]), ("class", counts["classes"]),
                                         ("ability", counts["abilities"]),
                                         ("story", counts["stories"])) if n]
    if not parts and report.problem_count > problems_before:
        return   # the problems above already explain why nothing loaded
    version = f" v{meta['version']}" if meta.get("version") else ""
    author  = f" by {meta['author']}" if meta.get("author") else ""
    report.ok(f"{title}{version}{author} - {', '.join(parts) if parts else 'loaded, but added nothing'}")


# ── Everything ────────────────────────────────────────────────
def load_content():
    """Load built-in stories, then every mod. Returns a LoadReport to show the player."""
    report = LoadReport()

    if os.path.isdir(STORIES_DIR):
        for f in sorted(os.listdir(STORIES_DIR)):
            if f.lower().endswith(".json"):
                try:
                    story_engine.load_story_file(os.path.join(STORIES_DIR, f), f"stories/{f}")
                except Exception as e:
                    report.problem(f"stories/{f}: {_describe_error(e)}")

    os.makedirs(MODS_DIR, exist_ok=True)
    for name in sorted(os.listdir(MODS_DIR)):
        folder = os.path.join(MODS_DIR, name)
        if os.path.isdir(folder) and not name.startswith(("_", ".")) and name != "__pycache__":
            _load_one_mod(folder, report)

    # Check stories last, so they can use monsters from any mod
    for title, story in list(story_engine.STORIES.items()):
        errors = story_engine.validate_story(story)
        if errors:
            del story_engine.STORIES[title]
            report.problem(f'Story "{title}" ({story["_label"]}) was skipped:')
            for e in errors:
                report.detail(e)
    return report
