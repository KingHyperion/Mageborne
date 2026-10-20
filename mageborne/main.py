import random

from game import Game
from player_classes import PLAYER_CLASSES


def fight(player, counts):
    Game(player, counts).run()


def choose_class_and_name():
    menu = "Please choose one of the classes below:\n" + "".join(
        f" {key}) {cls.class_name}: {cls.description}\n"
        for key, cls in PLAYER_CLASSES.items()
    )
    while True:
        choice = input(menu).strip().upper()
        if choice in PLAYER_CLASSES:
            break
        print("Please enter a valid option (A, B, or C)!")

    cls = PLAYER_CLASSES[choice]
    print("You have selected: " + cls.class_name)
    name = input("Please enter a name for your character: ")
    return cls(name)


def main():
    player = choose_class_and_name()
    player.describe()

    print("Welcome to Mageborne! Below is a little preface to the story (Beta Version)")
    print(
        f"Hello, {player.name}. You have been hired by the townspeople of Emberpine to investigate "
        "the nearby woods, after large monster tracks were found.\n"
        "The game starts with you at the entrance of the woods, where you'll walk through "
        "and face different types of monsters."
    )
    print("========================================\n")

    # ── Chapter 1: goblins ────────────────────────────────────
    menu_1 = (
        "What would you like to do?\n"
        " A) Search for clues\n"
        " B) Follow the trail\n"
        " C) Try to attract a monster\n"
    )
    path_1 = input("You enter the woods, " + menu_1[0].lower() + menu_1[1:]).strip().upper()

    done = False
    while not done:
        if path_1 == "A":
            roll = random.randint(1, 20) + (player.intelligence / 10)
            print("You rolled a " + str(roll) + " total for perception.")
            if roll >= 14:
                print("You find some torn fabric on the branches, leading towards a clearing. "
                      "Inside, stands 3 small goblins. Prepare for combat!")
                done = True
                fight(player, {"goblin": 3})
            else:
                print("You don't notice any evidence of monsters, "
                      "maybe you should try again or a different tactic.")
                path_1 = input(menu_1).strip().upper()

        elif path_1 == "B":
            print("You follow the trail and eventually find a log laying across it, "
                  "a further look reveals that it was deliberately placed there. "
                  "As you look around, you notice a new, smaller path leading towards a clearing. "
                  "Inside, stands 3 small goblins. Prepare for combat!")
            done = True
            fight(player, {"goblin": 3})

        elif path_1 == "C":
            print("You make some noise and lay out some aromatic food around you, hoping to attract "
                  "a monster. After a few minutes, you hear hushed voices leading towards a clearing. "
                  "Inside, stands 3 small goblins. Prepare for combat!")
            done = True
            fight(player, {"goblin": 3})

        else:
            print("Please enter a valid option (A, B, or C)!")
            path_1 = input(menu_1).strip().upper()

    # ── Chapter 2: Fairies ────────────────────────────────────
    player.level_up()
    menu_2 = (
        "What would you like to do?\n"
        " A) Inspect Goblin footprints\n"
        " B) Keep searching\n"
    )
    path_2 = input(menu_2).strip().upper()
    done = False
    while not done:
        if path_2 == "A":
            print("You take a look at the footprints left by the Goblins. It's clear they aren't the culprits of whatever was near town. As you begin to wonder who else could be guilty, you hear giggling up ahead. As you follow the noise, you come up on another clearing, this time with 2 fairies inside. Prepare for combat!")
            done = True
            fight(player, {"fairy": 2})
        elif path_2 == "B":
            print("As you look around, you notice some shimmering, magical dust on the branches. As you follow the dust's trail, you come up on another clearing, this time with 2 fairies inside. Prepare for combat!")
            done = True
            fight(player, {"fairy": 2})
        else:
            print("Please enter a valid option (A or B)!")
            path_2 = input(menu_2).strip().upper()

    # ── Chapter 3: Troll ──────────────────────────────────────
    player.level_up()
    menu_3 = (
        "What would you like to do?\n"
        " A) Inspect Fairy footprints\n"
        " B) Keep searching\n"
    )
    path_3 = input(menu_3).strip().upper()
    done = False
    while not done:
        if path_3 == "A":
            print("You take a look at the footprints left by the Fairies. It's clear they aren't the culprits of whatever was near town. As you begin to wonder who else could be guilty, you hear loud growling up ahead. As you follow the noise, you come up on another clearing, this time with a large Troll inside. Prepare for combat!")
            done = True
            fight(player, {"troll": 1})
        elif path_3 == "B":
            print("As you look around, you notice a large piece of fabric strung on a tree's branches, along with smoke rising ahead. As you the smoke towards the fabric, you come up on another clearing. This one has a large Troll inside. Prepare for combat!")
            done = True
            fight(player, {"troll": 1})
        else:
            print("Please enter a valid option (A or B)!")
            path_3 = input(menu_3).strip().upper()

    print("Once the Troll has been defeated, it's evident it was the culprit of those monster tracks.\n"
          "You head back to town to recieve your payment and deliver the good news, tired from your day of monster fighting.\n"
          "\n Congrats! You've successfully completed Mageborne: Beta Test Release! The full Godot version will be released soon, and the full base game afterwards.")


if __name__ == "__main__":
    main()
