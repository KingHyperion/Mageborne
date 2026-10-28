import math
import sys

from config import FLOOR, GRID_SIZE, REST_HEAL, REST_HEAL_PCT
from monsters import spawn_monsters
from ui import clear_screen, prompt_choice


class Game:
    def __init__(self, player, monster_counts=None):
        if monster_counts is None:
            monster_counts = {"goblin": 1, "archer": 1, "fairy": 1}

        self.player         = player
        self.grid           = [[FLOOR] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_x       = 0
        self.player_y       = 0
        self.max_hp         = player.health
        self.player_hp      = self.max_hp
        self.player_stunned = 0        # turns the player still has to skip
        self.guarding       = False    # True after choosing Guard, until monsters have acted
        self.hazards        = {}       # (x, y) -> {"emoji", "damage", "turns", "fresh"}  (e.g. fire)
        self.marks          = {}       # id(owner) -> (tiles, emoji, label)  (telegraphed danger zones)
        self.turn           = 1
        self.monsters       = spawn_monsters(monster_counts)
        self._needs_pause   = False

    # ══ Toolbox for monsters and abilities (this is what mods call) ═══════
    def say(self, text):
        """Show a message during the monsters' turn."""
        print("  " + text)
        self._needs_pause = True

    def dist(self, monster):
        """Distance from a monster to the player."""
        return math.dist((monster.x, monster.y), (self.player_x, self.player_y))

    def damage_player(self, amount):
        """Hurt the player (Guard halves it). Returns the damage actually dealt."""
        if self.guarding:
            amount = (amount + 1) // 2
        amount = max(0, amount)
        self.player_hp -= amount
        return amount

    def attack_player(self, monster):
        dealt = self.damage_player(monster.attack)
        note  = " (guarded)" if self.guarding else ""
        self.say(f"{monster.emoji} attacks you for {dealt} damage!{note}")

    def stun_player(self, turns):
        """Make the player skip their next `turns` turns."""
        self.player_stunned = max(self.player_stunned, turns)

    def add_hazard(self, tile, emoji="🔥", damage=2, turns=3):
        """Put a damaging tile on the grid. It hurts the player if they end a round standing on it."""
        self.hazards[tile] = {"emoji": emoji, "damage": damage, "turns": turns, "fresh": True}

    def mark(self, owner, tiles, emoji="🟥"):
        """Show a danger zone on the grid (purely visual - the ability decides what happens)."""
        self.marks[id(owner)] = (set(tiles), emoji, getattr(owner, "name", "something").title())

    def unmark(self, owner):
        self.marks.pop(id(owner), None)

    def occupied_tiles(self, exclude=None):
        return {(m.x, m.y) for m in self.monsters if m.alive and m is not exclude}

    def blocked_tiles(self, monster):
        """Tiles a monster can't walk onto: other monsters and the player."""
        return self.occupied_tiles(exclude=monster) | {(self.player_x, self.player_y)}

    # ══ Player actions (no input/output decisions in here) ═══════════════
    def heal_amount(self):
        return max(REST_HEAL, int(self.max_hp * REST_HEAL_PCT))

    def targets_in_range(self):
        return [
            m for m in self.monsters
            if m.alive and math.dist((self.player_x, self.player_y), (m.x, m.y)) <= self.player.atk_range
        ]

    def do_attack(self, target):
        dmg = self.player.attack
        target.hp -= dmg
        print(f"  You hit {target.emoji} for {dmg} dmg! ({max(target.hp, 0)} HP left)")
        if target.hp <= 0:
            target.alive = False
            self.unmark(target)
            print(f"  {target.emoji} defeated! 💥")

    def do_rest(self):
        healed = min(self.heal_amount(), self.max_hp - self.player_hp)
        self.player_hp += healed
        print(f"  You rest and recover {healed} HP. HP: {self.player_hp}/{self.max_hp}")

    def do_guard(self):
        self.guarding = True
        print("  You brace yourself - damage is halved until your next turn.")

    # ══ Rendering ═════════════════════════════════════════════════════════
    def render(self):
        clear_screen()
        alive = [m for m in self.monsters if m.alive]
        print(
            f"  Turn {self.turn}  |  ❤️  HP: {self.player_hp}/{self.max_hp}"
            f"  |  ⚔️  ATK: {self.player.attack}"
            f"  |  🎯 Range: {self.player.atk_range}"
            f"  |  👾 Remaining: {len(alive)}\n"
        )
        zone = {}
        for tiles, emoji, _ in self.marks.values():
            for t in tiles:
                zone[t] = emoji
        for row in range(GRID_SIZE):
            line = ""
            for col in range(GRID_SIZE):
                if col == self.player_x and row == self.player_y:
                    line += self.player.emoji
                    continue
                mon = next(
                    (m for m in self.monsters if m.alive and m.x == col and m.y == row),
                    None
                )
                if mon:
                    line += mon.emoji
                elif (col, row) in self.hazards:
                    line += self.hazards[(col, row)]["emoji"]
                else:
                    line += zone.get((col, row), self.grid[row][col])
            print(line)
        print()
        if self.player_stunned:
            print(f"  💫 You're stunned for {self.player_stunned} more turn(s)!")
        for _, emoji, label in self.marks.values():
            print(f"  {emoji} Danger zone - {label} is about to strike there!")
        for emoji in dict.fromkeys(h["emoji"] for h in self.hazards.values()):
            print(f"  {emoji} Hazard - ending your turn on it hurts.")
        idle = [m for m in alive
                if math.dist((m.x, m.y), (self.player_x, self.player_y)) > m.chase_radius]
        if idle:
            print("  💤 Idle (too far to notice you): " + " ".join(m.emoji for m in idle))
        print()

    # ══ Turn phases ═══════════════════════════════════════════════════════
    def player_turn(self):
        dirs = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
        moves_left = self.player.speed
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

    def action_phase(self):
        self.render()
        print("  Action phase")
        print(f"  [1] Attack   [2] Rest (+{self.heal_amount()} HP)   [3] Guard (half damage)\n")
        targets = self.targets_in_range()
        if targets:
            print("  Monsters in range: " + "  ".join(f"{m.emoji}({m.hp}hp)" for m in targets))
        else:
            print(f"  No monsters in range (your attack range is {self.player.atk_range} tile(s)).")
        print()
        choice = input("  > ").strip()
        if choice == "1":
            if not targets:
                print("  Nothing in range!")
            elif len(targets) == 1:
                self.do_attack(targets[0])
            else:
                print("\n  Attack which?")
                for i, m in enumerate(targets, 1):
                    print(f"  [{i}] {m.emoji} ({m.hp}hp)")
                pick = prompt_choice("", [str(i) for i in range(1, len(targets) + 1)])
                self.do_attack(targets[int(pick) - 1])
            input("  [Enter]")
        elif choice == "2":
            self.do_rest()
            input("  [Enter]")
        elif choice == "3":
            self.do_guard()
            input("  [Enter]")

    def monster_turn(self):
        for m in list(self.monsters):
            if self.player_hp <= 0:
                break
            if m.alive:
                m.take_turn(self)
        if self.player_hp > 0:
            self.resolve_hazards()
        self.guarding = False
        if self._needs_pause:
            input("  [Enter]")
            self._needs_pause = False

    def resolve_hazards(self):
        px, py = self.player_x, self.player_y
        for tile in list(self.hazards):
            h = self.hazards[tile]
            if h["fresh"]:                  # just created this round - starts hurting next round
                h["fresh"] = False
                continue
            if tile == (px, py):
                dealt = self.damage_player(h["damage"])
                self.say(f"{h['emoji']} You're burned for {dealt} damage!")
            h["turns"] -= 1
            if h["turns"] <= 0:
                del self.hazards[tile]

    # ══ Main loop ═════════════════════════════════════════════════════════
    def run(self):
        while self.player_hp > 0:
            if all(not m.alive for m in self.monsters):
                self.render()
                print("  🎉 All monsters defeated! You win!")
                input("\n  [Press Enter to continue your journey]")
                return
            if self.player_stunned > 0:
                self.render()
                print("  💫 You're stunned and can't act this turn!")
                self.player_stunned -= 1
                input("  [Enter]")
            else:
                self.player_turn()
                self.action_phase()
            self.monster_turn()
            self.turn += 1
        self.render()
        print("  💀 You have been defeated...")
        input("\n  [Press Enter to exit]")
        sys.exit()


def start_encounter(counts, player):
    Game(player, counts).run()
