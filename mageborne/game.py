import math
import os
import sys

from config import FLOOR, GRID_SIZE, MOVE_BUDGET, REST_HEAL, REST_CAP
from monsters import spawn_monsters


class Game:
    def __init__(self, player, monster_counts=None):
        if monster_counts is None:
            monster_counts = {"goblin": 1, "archer": 1, "fairy": 1}

        self.player           = player
        self.grid             = [[FLOOR] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_x         = 0
        self.player_y         = 0
        self.player_hp        = player.health
        self.turn             = 1
        self.monsters         = spawn_monsters(monster_counts)

    # ── Helpers ───────────────────────────────────────────────
    def occupied_tiles(self, exclude=None):
        return {(m.x, m.y) for m in self.monsters if m.alive and m is not exclude}

    # ── Rendering ─────────────────────────────────────────────
    def render(self):
        os.system("cls" if os.name == "nt" else "clear")
        alive = [m for m in self.monsters if m.alive]
        print(f"  Turn {self.turn}  |  ❤️  HP: {self.player_hp}  |  ⚔️  ATK: {self.player.attack}"
              f"  |  🎯 Range: {self.player.atk_range}  |  👾 Remaining: {len(alive)}\n")
        for row in range(GRID_SIZE):
            line = ""
            for col in range(GRID_SIZE):
                if col == self.player_x and row == self.player_y:
                    line += self.player.emoji
                    continue
                mon = next((m for m in self.monsters
                            if m.alive and m.x == col and m.y == row), None)
                line += mon.emoji if mon else self.grid[row][col]
            print(line)
        print()

    # ── Player movement ───────────────────────────────────────
    def player_turn(self):
        dirs = {"w": (0,-1), "s": (0,1), "a": (-1,0), "d": (1,0)}
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
                print("  Can't move there."); input("  [Enter]"); continue
            if any(m.alive and m.x == nx and m.y == ny for m in self.monsters):
                print("  A monster is blocking that tile!"); input("  [Enter]"); continue
            self.player_x, self.player_y = nx, ny
            moves_left -= 1

    # ── Action phase ──────────────────────────────────────────
    def action_phase(self):
        atk       = self.player.attack
        atk_range = self.player.atk_range

        self.render()
        print("  Action phase")
        print(f"  [1] Attack   [2] Rest (+{REST_HEAL} HP)   [3] Wait\n")
        targets = [
            m for m in self.monsters
            if m.alive and math.dist((self.player_x, self.player_y), (m.x, m.y)) <= atk_range
        ]
        if targets:
            print("  Monsters in range: "
                  + "  ".join(f"{m.emoji}({m.hp}hp)" for m in targets))
        else:
            print(f"  No monsters in range (your attack range is {atk_range} tile(s)).")
        print()
        choice = input("  > ").strip()
        if choice == "1":
            if not targets:
                print("  Nothing in range!")
            else:
                t = targets[0]
                t.hp -= atk
                print(f"  You hit {t.emoji} for {atk} dmg! ({max(t.hp, 0)} HP left)")
                if t.hp <= 0:
                    t.alive = False
                    print(f"  {t.emoji} defeated! 💥")
            input("  [Enter]")
        elif choice == "2":
            self.player_hp = min(self.player_hp + REST_HEAL, REST_CAP)
            print(f"  You rest. HP: {self.player_hp}")
            input("  [Enter]")

    # ── Monster turn ──────────────────────────────────────────
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

    # ── Main loop ─────────────────────────────────────────────
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
