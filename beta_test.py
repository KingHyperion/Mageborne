import random
import math
import os
import sys

# ── Tile emojis ───────────────────────────────────────────────────────────────
FLOOR = "🟫"

# ── Config ────────────────────────────────────────────────────────────────────
GRID_SIZE   = 6
MOVE_BUDGET = 2

# ── Monster roster ────────────────────────────────────────────────────────────
MONSTER_TYPES = {
    "goblin":   dict(emoji="👹",    hp=6,  attack=3, chase_radius=5, atk_min=1, atk_max=1),
    "archer":   dict(emoji="🏹",    hp=7,  attack=3, chase_radius=5, atk_min=2, atk_max=3),
    "fairy":    dict(emoji="🧿",    hp=8,  attack=5, chase_radius=6, atk_min=3, atk_max=4),
    "skeleton": dict(emoji="💀",    hp=10, attack=3, chase_radius=3, atk_min=1, atk_max=1),
    "dragon":   dict(emoji="🐉",    hp=25, attack=8, chase_radius=6, atk_min=2, atk_max=5),
    "snake":    dict(emoji="🐍",    hp=6,  attack=2, chase_radius=4, atk_min=1, atk_max=1),
    "troll":    dict(emoji="🧌",    hp=20, attack=6, chase_radius=3, atk_min=1, atk_max=1),
    "witch":    dict(emoji="🧙‍♀️", hp=9,  attack=7, chase_radius=6, atk_min=4, atk_max=5),
}


# ── Monster class ─────────────────────────────────────────────────────────────
class Monster:
    def __init__(self, x, y, emoji, hp, attack,
                 chase_radius, atk_min, atk_max):
        self.x, self.y    = x, y
        self.emoji        = emoji
        self.hp           = hp
        self.attack       = attack
        self.chase_radius = chase_radius
        self.atk_min      = atk_min
        self.atk_max      = atk_max
        self.alive        = True

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
            candidates = [(self.x + dx, self.y), (self.x, self.y + dy)]
        else:
            candidates = [(self.x, self.y + dy), (self.x + dx, self.y)]
        for nx, ny in candidates:
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in occupied:
                self.x, self.y = nx, ny
                return

    def can_attack(self, px, py):
        return self.atk_min <= math.dist((self.x, self.y), (px, py)) <= self.atk_max

    def is_adjacent(self, px, py):
        return abs(self.x - px) <= 1 and abs(self.y - py) <= 1


# ── Spawn helper ──────────────────────────────────────────────────────────────
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
            raise ValueError(
                f"Unknown monster type '{name}'. "
                f"Choose from: {list(MONSTER_TYPES.keys())}"
            )
        stats = MONSTER_TYPES[name]
        for _ in range(count):
            try:
                x, y = next(tile_pool)
            except StopIteration:
                raise ValueError("Too many monsters for the grid size!")
            monsters.append(Monster(x, y, **stats))

    return monsters


# ── Game class ────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, monster_counts=None, player_hp=30, player_atk=5,
                 player_atk_range=1, player_emoji="🧙"):
        if monster_counts is None:
            monster_counts = {"goblin": 1, "archer": 1, "fairy": 1}

        self.grid             = [[FLOOR] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_x         = 0
        self.player_y         = 0
        self.player_hp        = player_hp
        self.player_atk       = player_atk
        self.player_atk_range = player_atk_range
        self.player_emoji     = player_emoji
        self.turn             = 1
        self.monsters         = spawn_monsters(monster_counts)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def occupied_tiles(self, exclude=None):
        return {(m.x, m.y) for m in self.monsters if m.alive and m is not exclude}

    # ── Rendering ─────────────────────────────────────────────────────────────
    def render(self):
        os.system("cls" if os.name == "nt" else "clear")
        alive = [m for m in self.monsters if m.alive]
        print(
            f"  Turn {self.turn}  |  ❤️  HP: {self.player_hp}"
            f"  |  ⚔️  ATK: {self.player_atk}"
            f"  |  🎯 Range: {self.player_atk_range}"
            f"  |  👾 Remaining: {len(alive)}\n"
        )
        for row in range(GRID_SIZE):
            line = ""
            for col in range(GRID_SIZE):
                if col == self.player_x and row == self.player_y:
                    line += self.player_emoji
                    continue
                mon = next(
                    (m for m in self.monsters if m.alive and m.x == col and m.y == row),
                    None
                )
                line += mon.emoji if mon else self.grid[row][col]
            print(line)
        print()

    # ── Player movement ───────────────────────────────────────────────────────
    def player_turn(self):
        dirs = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        moves_left = MOVE_BUDGET
        while moves_left > 0:
            self.render()
            print(f"  Move phase — {moves_left} step(s) left")
            print("  [W/A/S/D] move   [Enter] skip remaining steps\n")
            key = input("  > ").strip().lower()
            if key == "":
                break
            if key not in dirs:
                continue
            dx, dy = dirs[key]
            nx, ny = self.player_x + dx, self.player_y + dy
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                print("  Can't move there.")
                input("  [Enter]")
                continue
            if any(m.alive and m.x == nx and m.y == ny for m in self.monsters):
                print("  A monster is blocking that tile!")
                input("  [Enter]")
                continue
            self.player_x, self.player_y = nx, ny
            moves_left -= 1

    # ── Action phase ──────────────────────────────────────────────────────────
    def action_phase(self):
        self.render()
        print("  Action phase")
        print("  [1] Attack   [2] Rest (+3 HP)   [3] Wait\n")
        targets = [
            m for m in self.monsters
            if m.alive and math.dist(
                (self.player_x, self.player_y), (m.x, m.y)
            ) <= self.player_atk_range
        ]
        if targets:
            print("  Monsters in range: "
                  + "  ".join(f"{m.emoji}({m.hp}hp)" for m in targets))
        else:
            print(f"  No monsters in range (your attack range is {self.player_atk_range} tile(s)).")
        print()
        choice = input("  > ").strip()
        if choice == "1":
            if not targets:
                print("  Nothing in range!")
            else:
                t = targets[0]
                t.hp -= self.player_atk
                print(f"  You hit {t.emoji} for {self.player_atk} dmg! ({max(t.hp, 0)} HP left)")
                if t.hp <= 0:
                    t.alive = False
                    print(f"  {t.emoji} defeated! 💥")
            input("  [Enter]")
        elif choice == "2":
            self.player_hp = min(self.player_hp + 3, 30)
            print(f"  You rest. HP: {self.player_hp}")
            input("  [Enter]")

    # ── Monster turn ──────────────────────────────────────────────────────────
    def monster_turn(self):
        attacked = False
        for m in self.monsters:
            if not m.alive:
                continue
            blocked = self.occupied_tiles(exclude=m)
            blocked.add((self.player_x, self.player_y))
            m.move_toward(self.player_x, self.player_y, blocked)
            if m.can_attack(self.player_x, self.player_y):
                self.player_hp -= m.attack
                print(f"  {m.emoji} attacks you for {m.attack} damage!")
                attacked = True
        if attacked:
            input("  [Enter]")

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        while self.player_hp > 0:
            if all(not m.alive for m in self.monsters):
                self.render()
                print("  🎉 All monsters defeated! You win!")
                return
            self.player_turn()
            self.action_phase()
            self.monster_turn()
            self.turn += 1
        self.render()
        print("  💀 You have been defeated...")
        sys.exit()


# ── Launch helper ─────────────────────────────────────────────────────────────
def start_encounter(counts, player_hp, player_atk, player_atk_range, player_emoji):
    Game(
        counts,
        player_hp=player_hp,
        player_atk=player_atk,
        player_atk_range=player_atk_range,
        player_emoji=player_emoji,
    ).run()


# ── Helper: prompt until valid choice ────────────────────────────────────────
def prompt_choice(prompt, valid_options):
    """Repeatedly prompt until the player enters one of valid_options (uppercase)."""
    while True:
        choice = input(prompt).strip().upper()
        if choice in valid_options:
            return choice
        valid_str = ", ".join(valid_options)
        print(f"  Please enter a valid option ({valid_str})!")


# ── Helper: compute HP from level and constitution ────────────────────────────
def calc_hp(level, constitution):
    return int(10 * level + constitution / 10)


# ═════════════════════════════════════════════════════════════════════════════
# Game start
# ═════════════════════════════════════════════════════════════════════════════

# ── Class selection ───────────────────────────────────────────────────────────
CLASS_PROMPT = (
    "Please choose one of the classes below:\n"
    "  A) Warrior: A martial fighter, focusing on strength.\n"
    "  B) Mage: An arcane user of magic, focusing on intelligence but with low health.\n"
    "  C) Thief: A cunning rogue, focusing on stealth to sneak around.\n"
)

CLASSES = {
    "A": dict(
        name="Warrior", emoji="🤺",
        strength=15, dexterity=14, constitution=13, intelligence=8,
        attack=4, atk_range=1,
    ),
    "B": dict(
        name="Mage", emoji="🧙",
        strength=8, dexterity=12, constitution=13, intelligence=15,
        attack=5, atk_range=5,
    ),
    "C": dict(
        name="Thief", emoji="🥷🏻",
        strength=12, dexterity=15, constitution=13, intelligence=14,
        attack=3, atk_range=3,
    ),
}

level_p        = 1
selection      = prompt_choice(CLASS_PROMPT, CLASSES.keys())
cls            = CLASSES[selection]
player_class   = cls["name"]
player_emoji_p = cls["emoji"]
strength_p     = cls["strength"]
dexterity_p    = cls["dexterity"]
constitution_p = cls["constitution"]
intelligence_p = cls["intelligence"]
attack_p       = cls["attack"]
atk_range_p    = cls["atk_range"]
health_p       = calc_hp(level_p, constitution_p)

print(f"\nYou have selected: {player_class}")
name_p = input("Please enter a name for your character: ")
print(
    f"\nPlayer description:\n"
    f"  Name:          {name_p}\n"
    f"  Class:         {player_class}\n"
    f"  Health:        {health_p}\n"
    f"  Attack:        {attack_p}\n"
    f"  Attack Range:  {atk_range_p}\n"
    f"  Strength:      {strength_p}\n"
    f"  Dexterity:     {dexterity_p}\n"
    f"  Constitution:  {constitution_p}\n"
    f"  Intelligence:  {intelligence_p}\n"
    f"  {'=' * 40}"
)

# ── Introduction ──────────────────────────────────────────────────────────────
print("Welcome to Mageborne! Below is a little preface to the story (Beta Version)\n")
print(
    f"Hello, {name_p}. You have been hired by the townspeople of Emberpine to investigate\n"
    "the nearby woods, after large monster tracks were found.\n"
    "The game starts with you at the entrance of the woods, where you'll walk through\n"
    "and face different types of monsters."
)
print(f"\n{'=' * 40}\n")

# ── Chapter 1: The Woods ──────────────────────────────────────────────────────
CHAPTER1_PROMPT = (
    "You enter the woods, what would you like to do?\n"
    "  A) Search for clues\n"
    "  B) Follow the trail\n"
    "  C) Try to attract a monster\n"
)

path_1 = prompt_choice(CHAPTER1_PROMPT, {"A", "B", "C"})

while True:
    if path_1 == "A":
        roll = random.randint(1, 20) + intelligence_p / 10
        print(f"  You rolled a {roll:.1f} total for perception.")
        if roll >= 14:
            print(
                "  You find some torn fabric on the branches, leading towards a clearing.\n"
                "  Inside, stands 3 small goblins. Prepare for combat!"
            )
            start_encounter(
                {"goblin": 3}, player_hp=health_p, player_atk=attack_p,
                player_atk_range=atk_range_p, player_emoji=player_emoji_p,
            )
            break
        else:
            print("  You don't notice any evidence of monsters — maybe try again or a different tactic.")
            path_1 = prompt_choice(CHAPTER1_PROMPT, {"A", "B", "C"})

    elif path_1 == "B":
        print(
            "  You follow the trail and eventually find a log laying across it.\n"
            "  A further look reveals it was deliberately placed there.\n"
            "  As you look around, you notice a smaller path leading to a clearing.\n"
            "  Inside, stands 3 small goblins. Prepare for combat!"
        )
        start_encounter(
            {"goblin": 3}, player_hp=health_p, player_atk=attack_p,
            player_atk_range=atk_range_p, player_emoji=player_emoji_p,
        )
        break

    elif path_1 == "C":
        print(
            "  You make some noise and lay out aromatic food around you, hoping to attract a monster.\n"
            "  After a few minutes, you hear hushed voices leading towards a clearing.\n"
            "  Inside, stands 3 small goblins. Prepare for combat!"
        )
        start_encounter(
            {"goblin": 3}, player_hp=health_p, player_atk=attack_p,
            player_atk_range=atk_range_p, player_emoji=player_emoji_p,
        )
        break

# ── Level up: 1 → 2 ───────────────────────────────────────────────────────────
level_p  = 2
health_p = calc_hp(level_p, constitution_p)
print(f"\n  Congratulations! You're now level {level_p}.\n")

# ── Chapter 2: The Fairies ────────────────────────────────────────────────────
CHAPTER2_PROMPT = (
    "What would you like to do?\n"
    "  A) Inspect goblin footprints\n"
    "  B) Keep searching\n"
)

path_2 = prompt_choice(CHAPTER2_PROMPT, {"A", "B"})

while True:
    if path_2 == "A":
        print(
            "  You examine the footprints left by the goblins — clearly not the culprits.\n"
            "  As you wonder who else could be responsible, you hear giggling up ahead.\n"
            "  Following the sound, you come upon a clearing with 2 fairies inside. Prepare for combat!"
        )
        start_encounter(
            {"fairy": 2}, player_hp=health_p, player_atk=attack_p,
            player_atk_range=atk_range_p, player_emoji=player_emoji_p,
        )
        break

    elif path_2 == "B":
        print(
            "  As you look around, you notice shimmering magical dust on the branches.\n"
            "  Following the trail, you come upon a clearing with 2 fairies inside. Prepare for combat!"
        )
        start_encounter(
            {"fairy": 2}, player_hp=health_p, player_atk=attack_p,
            player_atk_range=atk_range_p, player_emoji=player_emoji_p,
        )
        break

# ── Level up: 2 → 3 ───────────────────────────────────────────────────────────
level_p  = 3
health_p = calc_hp(level_p, constitution_p)
print(f"\n  Congratulations! You're now level {level_p}.\n")

# ── Chapter 3: The Troll ──────────────────────────────────────────────────────
CHAPTER3_PROMPT = (
    "What would you like to do?\n"
    "  A) Inspect fairy footprints\n"
    "  B) Keep searching\n"
)

path_3 = prompt_choice(CHAPTER3_PROMPT, {"A", "B"})

while True:
    if path_3 == "A":
        print(
            "  You examine the footprints left by the fairies — not the culprits either.\n"
            "  As you wonder who is truly responsible, you hear loud growling up ahead.\n"
            "  Following the noise, you come upon a clearing with a large Troll inside. Prepare for combat!"
        )
        start_encounter(
            {"troll": 1}, player_hp=health_p, player_atk=attack_p,
            player_atk_range=atk_range_p, player_emoji=player_emoji_p,
        )
        break

    elif path_3 == "B":
        print(
            "  You notice a large piece of fabric strung on the branches, along with smoke rising ahead.\n"
            "  Following the smoke, you come upon a clearing with a large Troll inside. Prepare for combat!"
        )
        start_encounter(
            {"troll": 1}, player_hp=health_p, player_atk=attack_p,
            player_atk_range=atk_range_p, player_emoji=player_emoji_p,
        )
        break

# ── Ending ────────────────────────────────────────────────────────────────────
print(
    "\n  Once the Troll has been defeated, it's evident it was the culprit behind those monster tracks.\n"
    "  You head back to town to receive your payment and deliver the good news,\n"
    "  tired but victorious from your day of monster fighting.\n"
    "\n  Congratulations! You've successfully completed Mageborne: Beta Test Release!\n"
    "  The full Godot version will be released soon, and the full base game afterwards."
)
