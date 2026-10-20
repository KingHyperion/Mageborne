import random

from config import GRID_SIZE
from .registry import MONSTER_TYPES


def spawn_monsters(counts):
    safe_tiles = [
        (x, y)
        for x in range(GRID_SIZE)
        for y in range(GRID_SIZE)
        if not (x <= 1 and y <= 1)
    ]
    random.shuffle(safe_tiles)
    tile_pool = iter(safe_tiles)

    monsters = []
    for name, count in counts.items():
        if count == 0:
            continue
        if name not in MONSTER_TYPES:
            raise ValueError(f"Unknown monster type '{name}'. "
                             f"Choose from: {list(MONSTER_TYPES.keys())}")
        monster_cls = MONSTER_TYPES[name]
        for _ in range(count):
            try:
                x, y = next(tile_pool)
            except StopIteration:
                raise ValueError("Too many monsters for the grid size!")
            monsters.append(monster_cls(x, y))

    return monsters
