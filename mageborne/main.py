import random
import os
from mageborne.game import start_encounter
from mageborne.player_classes import CLASSES
from mageborne.player import calc_hp

def prompt_choice(prompt, valid_options):
    while True:
        choice = input(prompt).strip().upper()
        if choice in valid_options:
            return choice
        valid_str = ", ".join(sorted(valid_options))
        print(f"  Please enter a valid option ({valid_str})!")

def main():
    CLASS_PROMPT = (
        "Please choose one of the classes below:\n"
        "  A) Warrior: A martial fighter, focusing on strength.\n"
        "  B) Mage: An arcane user of magic, focusing on intelligence but with low health.\n"
        "  C) Thief: A cunning rogue, focusing on stealth to sneak around.\n"
    )

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
    input("\n  [Press Enter to begin your adventure]")

    os.system("cls" if os.name == "nt" else "clear")
    print("Welcome to Mageborne! Below is a little preface to the story (Beta Version)\n")
    print(
        f"Hello, {name_p}. You have been hired by the townspeople of Emberpine to investigate\n"
        "the nearby woods, after large monster tracks were found.\n"
        "The game starts with you at the entrance of the woods, where you'll walk through\n"
        "and face different types of monsters."
    )
    print(f"\n{'=' * 40}")
    input("\n  [Press Enter to enter the woods]")

    CHAPTER1_PROMPT = (
        "\nYou enter the woods, what would you like to do?\n"
        "  A) Search for clues\n"
        "  B) Follow the trail\n"
        "  C) Try to attract a monster\n"
    )

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        path_1 = prompt_choice(CHAPTER1_PROMPT, {"A", "B", "C"})

        if path_1 == "A":
            roll = random.randint(1, 20) + intelligence_p / 10
            print(f"\n  You rolled a {roll:.1f} total for perception.")
            if roll >= 14:
                print(
                    "  You find some torn fabric on the branches, leading towards a clearing.\n"
                    "  Inside, stands 3 small goblins. Prepare for combat!"
                )
                input("\n  [Press Enter to start combat]")
                start_encounter(
                    {"goblin": 3}, player_hp=health_p, player_atk=attack_p,
                    player_atk_range=atk_range_p, player_emoji=player_emoji_p,
                )
                break
            else:
                print("  You don't notice any evidence of monsters — searching again...")
                input("\n  [Press Enter to try another tactic]")

        elif path_1 == "B":
            print(
                "\n  You follow the trail and eventually find a log laying across it.\n"
                "  A further look reveals it was deliberately placed there.\n"
                "  As you look around, you notice a smaller path leading to a clearing.\n"
                "  Inside, stands 3 small goblins. Prepare for combat!"
            )
            input("\n  [Press Enter to start combat]")
            start_encounter(
                {"goblin": 3}, player_hp=health_p, player_atk=attack_p,
                player_atk_range=atk_range_p, player_emoji=player_emoji_p,
            )
            break

        elif path_1 == "C":
            print(
                "\n  You make some noise and lay out aromatic food around you, hoping to attract a monster.\n"
                "  After a few minutes, you hear hushed voices leading towards a clearing.\n"
                "  Inside, stands 3 small goblins. Prepare for combat!"
            )
            input("\n  [Press Enter to start combat]")
            start_encounter(
                {"goblin": 3}, player_hp=health_p, player_atk=attack_p,
                player_atk_range=atk_range_p, player_emoji=player_emoji_p,
            )
            break

    level_p  = 2
    health_p = calc_hp(level_p, constitution_p)
    os.system("cls" if os.name == "nt" else "clear")
    print(f"\n  🎉 Congratulations! You're now level {level_p}.\n")
    input("  [Press Enter to continue to Chapter 2]")

    CHAPTER2_PROMPT = (
        "\nWhat would you like to do?\n"
        "  A) Inspect goblin footprints\n"
        "  B) Keep searching\n"
    )

    os.system("cls" if os.name == "nt" else "clear")
    path_2 = prompt_choice(CHAPTER2_PROMPT, {"A", "B"})

    if path_2 == "A":
        print(
            "\n  You examine the footprints left by the goblins — clearly not the culprits.\n"
            "  As you wonder who else could be responsible, you hear giggling up ahead.\n"
            "  Following the sound, you come upon a clearing with 2 fairies inside. Prepare for combat!"
        )
    else:
        print(
            "\n  As you look around, you notice shimmering magical dust on the branches.\n"
            "  Following the trail, you come upon a clearing with 2 fairies inside. Prepare for combat!"
        )

    input("\n  [Press Enter to start combat]")
    start_encounter(
        {"fairy": 2}, player_hp=health_p, player_atk=attack_p,
        player_atk_range=atk_range_p, player_emoji=player_emoji_p,
    )

    level_p  = 3
    health_p = calc_hp(level_p, constitution_p)
    os.system("cls" if os.name == "nt" else "clear")
    print(f"\n  🎉 Congratulations! You're now level {level_p}.\n")
    input("  [Press Enter to continue to Chapter 3]")

    CHAPTER3_PROMPT = (
        "\nWhat would you like to do?\n"
        "  A) Inspect fairy footprints\n"
        "  B) Keep searching\n"
    )

    os.system("cls" if os.name == "nt" else "clear")
    path_3 = prompt_choice(CHAPTER3_PROMPT, {"A", "B"})

    if path_3 == "A":
        print(
            "\n  You examine the footprints left by the fairies — not the culprits either.\n"
            "  As you wonder who is truly responsible, you hear loud growling up ahead.\n"
            "  Following the noise, you come upon a clearing with a large Troll inside. Prepare for combat!"
        )
    else:
        print(
            "\n  You notice a large piece of fabric strung on the branches, along with smoke rising ahead.\n"
            "  Following the smoke, you come upon a clearing with a large Troll inside. Prepare for combat!"
        )

    input("\n  [Press Enter to start boss combat]")
    start_encounter(
        {"troll": 1}, player_hp=health_p, player_atk=attack_p,
        player_atk_range=atk_range_p, player_emoji=player_emoji_p,
    )

    os.system("cls" if os.name == "nt" else "clear")
    print(
        "\n  Once the Troll has been defeated, it's evident it was the culprit behind those monster tracks.\n"
        "  You head back to town to receive your payment and deliver the good news,\n"
        "  tired but victorious from your day of monster fighting.\n"
        "\n  Congratulations! You've successfully completed Mageborne: Beta Test Release!\n"
        "  The full Godot version will be released soon, and the full base game afterwards."
    )
    input("\n  [Press Enter to exit]")

if __name__ == "__main__":
    main()