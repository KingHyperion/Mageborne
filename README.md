# Mageborne

A turn-based, text-mode RPG played on a small emoji grid, written in plain Python with zero external dependencies. Pick a class, play through a story, and fight monsters in tactical grid battles where positioning, healing, and dodging actually matter.

The entire game is **moddable**: anyone can add custom monsters (even with special abilities), character classes, and full storylines just by dropping a folder into `mods/`. Most mods don't even require writing any code.

```text
🤺🟫🟫🟫🟫🟫      Turn 3  |  ❤️  HP: 24/40  |  ⚔️  ATK: 7  |  🎯 Range: 1  |  👾 Remaining: 1
🟫🟫🟫🟫🟫🟫
🟫🟫🟫🟥🟥🟥      🟥 Danger zone - Troll is about to strike there!
🟫🟫🟫🟥🗿🟥
🟫🟫🟫🟥🟥🟥
🟫🟫🟫🟫🟫🟫
```

---

## Quick Start

**Requirements:** Python 3.8 or newer, and a terminal that handles emojis. There's nothing to install.

**How to run it:**
* **From your editor:** Open the `mageborne` folder in VS Code, Thonny, or PyCharm, open `main.py`, and hit run.
* **By double-clicking:** Open `main.py` directly if your system is set up to run Python files (it'll need a console window to draw the grid).
* **From the terminal:** `python main.py` (or `python3 main.py`) inside the `mageborne` directory.

You'll be prompted to pick a class, name your character, and dive straight into the story.

---

## How to Play

### The Grid
Fights take place on a **6x6 grid**. You start in the top-left corner, and monsters spawn randomly everywhere except the 2x2 area right around you.

| Symbol | Meaning |
| :--- | :--- |
| `🟫` | Empty floor |
| Your class emoji | You (🤺 Warrior, 🧙 Mage, 🥷 Thief, etc.) |
| Monster emoji | A monster (👹 Goblin, 🧿 Fairy, 🗿 Troll, etc.) |
| `🟥` | **Danger zone:** A monster is about to hit these tiles—get out of the way! |
| `🔥` | **Fire:** Ending your turn here hurts |
| `💤` (Below grid) | Idle monsters (they're too far away to notice you yet) |
| `💫` (Below grid) | Stunned status (you'll skip turns) |

### A Single Round
Each round has three quick phases:
1. **Move:** Walk up to your **speed** in tiles using **W / A / S / D**. Press **Enter** to stop early. You can't walk through monsters.
2. **Action:** Choose one:
   * **`1` Attack:** Hit a monster within your attack range. (If multiple are in range, you choose the target.)
   * **`2` Rest:** Heal 20% of your max HP (at least 3).
   * **`3` Guard:** Take half damage from all incoming hits until your next turn.
   * *Anything else:* Do nothing.
3. **Monsters Act:** Each monster uses an ability if ready, or lumbers toward you and attacks if you're in range. Lingering fire then burns anyone standing on it.

You win when every monster bites the dust. If your HP hits 0, it's game over. **Your HP fully restores at the start of every new fight.**

### Distance and Range
Distances are calculated in straight lines (diagonal steps count as roughly 1.41 tiles):
* **Melee (Range 1) is strictly orthogonal:** Up, down, left, right. A monster standing diagonally from you can't hit you, and you can't hit it.
* **Ranged attackers** (Mages, Thieves, archers, etc.) work at any angle within their specified range.
* **Chase radius:** Monsters stay put and display as idle (`💤`) until you step within their awareness radius.

### Stats and Leveling
* **Constitution:** Determines your max health (`8 x level + constitution`).
* **Intelligence / Strength / Dexterity:** Used for narrative skill checks throughout the story or mods.
* **Attack & Range:** Damage dealt per hit and how far away you can strike.
* **Speed:** Tiles you can walk per round.

You level up after specific story fights, raising your maximum health along the way.

---

## Classes

| Class | Emoji | Attack | Range | Speed | Core Stats (Str / Dex / Con / Int) | HP (Levels 1 / 2 / 3) |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Warrior** | 🤺 | 7 | 1 | 2 | 15 / 11 / 16 / 8 | 24 / 32 / 40 |
| **Mage** | 🧙 | 6 | 4 | 2 | 8 / 12 / 12 / 17 | 20 / 28 / 36 |
| **Thief** | 🥷 | 5 | 3 | 3 | 12 / 15 / 13 / 14 | 21 / 29 / 37 |

* **Warrior:** Hits the hardest and has the most health, but has to stay up close and personal.
* **Mage:** Fragile, but excels at slinging spells from afar.
* **Thief:** Lightning fast, making it easy to dodge danger zones and slip away.

---

## Monsters

| Monster | Emoji | HP | Damage | Chase Radius | Attack Range | Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Goblin** | 👹 | 8 | 4 | 5 | 1 | Basic melee |
| **Archer** | 🏹 | 7 | 3 | 5 | 2–3 | Ranged; keeps its distance |
| **Fairy** | 🧿 | 18 | 7 | 6 | 3–4 | Ranged; keeps its distance |
| **Skeleton** | 💀 | 10 | 3 | 3 | 1 | Melee |
| **Snake** | 🐍 | 6 | 2 | 4 | 1 | Melee |
| **Witch** | 🔮 | 9 | 7 | 6 | 4–5 | Long-range caster |
| **Dragon** | 🐉 | 25 | 8 | 6 | 2–5 | **Fire Breath:** Deals 6 damage in a line and leaves fire for 3 turns. |
| **Troll** | 🗿 | 30 | 5 | 8 | 1 | Moves 2 tiles/round. **Ground Pound**; enrages at half health. |

---

## The Built-In Story

**Mageborne: The Emberpine Woods** is a brief three-chapter adventure where you investigate local woods after massive monster tracks turn up:
1. **Goblins:** Search for clues using an Intelligence check, follow the trail, or try flushing them out. 
2. **Fairies:** Investigate footprints or press deeper into the forest.
3. **The Troll:** Face off against the boss of the woods.

---

## Modding

Want to add your own content? Just drop a folder inside `mods/`. 
* Rename `mods/_example_mod` to `example_mod` to check out a working example containing a custom class, monsters, abilities, and a story script.
* You can write simple mods entirely in JSON (no Python required), or write Python scripts for advanced custom mechanics.
* To temporarily disable a mod, just prefix its folder name with an underscore (`_`).

Read the complete guide in **[`mods/README.md`](mods/README.md)** for full documentation on custom fields and settings.

---

## Troubleshooting

* **Misaligned Grid/Emojis:** Some terminal fonts stretch certain emojis. Stick to single-character emojis for the best visual experience.
* **`ModuleNotFoundError`:** Make sure you're running `main.py` directly from within the `mageborne` root directory.
* **Mod Not Showing Up:** Ensure the folder lives directly inside `mods/`, doesn't start with an underscore or period, and has its files sitting right at the root level of that folder.
* **Monster Won't Move:** It's likely idling outside its chase radius. Check for the `💤` indicator below the grid.