import math

from config import GRID_SIZE


class Monster:
    """Base class for every monster.

    Subclasses override the class attributes below to change HP,
    damage, chase radius, and attack range.
    """

    name         = "monster"
    emoji        = "👾"
    max_hp       = 5
    attack       = 2
    chase_radius = 4
    atk_min      = 1
    atk_max      = 1

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.hp        = self.max_hp
        self.alive     = True

    def move_toward(self, px, py, occupied):
        dist = math.dist((self.x, self.y), (px, py))
        if dist > self.chase_radius:
            return
        if dist > self.atk_max:
            self._step(px, py, occupied, approach=True)
        elif dist < self.atk_min:
            self._step(px, py, occupied, approach=False)

    def _step(self, px, py, occupied, approach):
        dx = 0 if px == self.x else int(math.copysign(1, px - self.x))
        dy = 0 if py == self.y else int(math.copysign(1, py - self.y))
        if not approach:
            dx, dy = -dx, -dy
        if abs(px - self.x) >= abs(py - self.y):
            candidates = [(self.x+dx, self.y), (self.x, self.y+dy)]
        else:
            candidates = [(self.x, self.y+dy), (self.x+dx, self.y)]
        for nx, ny in candidates:
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in occupied:
                self.x, self.y = nx, ny
                return

    def can_attack(self, px, py):
        return self.atk_min <= math.dist((self.x, self.y), (px, py)) <= self.atk_max

    def is_adjacent(self, px, py):
        return abs(self.x - px) <= 1 and abs(self.y - py) <= 1
