"""Saving and loading progress.

The game saves automatically at the start of every story scene (a "checkpoint"), so closing the
window never loses more than the scene you were in. Each character gets one small JSON file in saves/.
"""
import json
import os
import re
import time

from config import SAVES_DIR

SAVE_VERSION = 1


class SaveError(Exception):
    """A save couldn't be used; the message is written for the player."""


def slugify(text, fallback="player"):
    slug = re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_")
    return slug or fallback


def save_path(player_name):
    return os.path.join(SAVES_DIR, slugify(player_name) + ".json")


def save_exists(player_name):
    return os.path.isfile(save_path(player_name))


def write_save(player, story, scene_id, completed=False):
    """Write (or update) the save for this character. Returns the file path."""
    os.makedirs(SAVES_DIR, exist_ok=True)
    data = {
        "version":   SAVE_VERSION,
        "saved_at":  time.strftime("%Y-%m-%d %H:%M"),
        "story":     story["title"],
        "scene":     scene_id,
        "completed": bool(completed),
        "player":    {"name": player.name, "class": player.class_name, "level": player.level},
    }
    path = save_path(player.name)
    tmp  = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)            # never leaves a half-written save behind
    return path


def read_save(path):
    """Read and shape-check one save file. Raises SaveError with a friendly message."""
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        raise SaveError(f"{name} couldn't be read ({e}).")
    try:
        player = data["player"]
        info = {
            "path":      path,
            "name":      str(player["name"]),
            "class":     str(player["class"]),
            "level":     int(player["level"]),
            "story":     str(data["story"]),
            "scene":     str(data["scene"]),
            "completed": bool(data.get("completed", False)),
            "saved_at":  str(data.get("saved_at", "")),
        }
    except (KeyError, TypeError, ValueError):
        raise SaveError(f"{name} is missing some information, so it can't be used.")
    return info


def list_saves():
    """Every save in saves/, newest first. Unreadable ones come back as {"path", "error"}."""
    if not os.path.isdir(SAVES_DIR):
        return []
    found = []
    for fname in os.listdir(SAVES_DIR):
        if not fname.lower().endswith(".json"):
            continue
        path = os.path.join(SAVES_DIR, fname)
        try:
            found.append(read_save(path))
        except SaveError as e:
            found.append({"path": path, "error": str(e)})
    found.sort(key=lambda s: os.path.getmtime(s["path"]), reverse=True)
    return found


def resolve_save(info, stories, classes):
    """Turn a save into (story, player, scene_id), or raise SaveError saying what's missing."""
    story = stories.get(info["story"])
    if story is None:
        raise SaveError(f'This save needs the story "{info["story"]}", which isn\'t installed. '
                        f'If it came from a mod, put that mod back in the mods folder.')
    cls = classes.get(info["class"])
    if cls is None:
        raise SaveError(f'This save uses the class "{info["class"]}", which isn\'t installed. '
                        f'If it came from a mod, put that mod back in the mods folder.')
    if info["scene"] not in story["scenes"]:
        raise SaveError(f'The scene "{info["scene"]}" no longer exists in "{info["story"]}" '
                        f'(the story was probably edited), so this save can\'t be continued.')
    return story, cls(info["name"], info["level"]), info["scene"]
