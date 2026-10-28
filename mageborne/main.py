from mod_loader import load_content
from player_classes import PLAYER_CLASSES
from story import STORIES, run_story
from ui import menu_keys, prompt_choice


def show_load_report(report):
    if not report.lines:
        return                      # no mods installed - say nothing
    print("Mods:")
    print("\n".join(report.lines))
    if report.has_problems:
        input("\n  [Some mod content was skipped - press Enter to continue]")
    print()


def choose_story():
    stories = list(STORIES.values())
    if len(stories) == 1:
        return stories[0]           # only the built-in story - no menu needed
    keys = menu_keys(len(stories))
    lines = []
    for key, s in zip(keys, stories):
        extra = " - " + s["description"] if s.get("description") else ""
        by    = f" (by {s['author']})" if s.get("author") else ""
        lines.append(f"  {key}) {s['title']}{by}{extra}\n")
    return stories[keys.index(prompt_choice("Choose your adventure:\n" + "".join(lines), keys))]


def choose_class():
    classes = list(PLAYER_CLASSES.values())
    keys    = menu_keys(len(classes))
    prompt  = "Please choose one of the classes below:\n" + "".join(
        f"  {k}) {c.class_name}: {c.description}\n" for k, c in zip(keys, classes)
    )
    return classes[keys.index(prompt_choice(prompt, keys))]


def main():
    report = load_content()
    show_load_report(report)
    if not STORIES:
        print("No playable story was found - check the messages above.")
        input("\n  [Press Enter to exit]")
        return

    story = choose_story()
    cls   = choose_class()

    print(f"\nYou have selected: {cls.class_name}")
    player = cls(input("Please enter a name for your character: "))
    player.describe()
    input("\n  [Press Enter to begin your adventure]")

    run_story(story, player)


if __name__ == "__main__":
    main()
