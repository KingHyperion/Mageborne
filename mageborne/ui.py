import os
import string


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def menu_keys(count):
    """A, B, C... for up to 26 options, then 1, 2, 3... for bigger menus."""
    if count <= 26:
        return list(string.ascii_uppercase[:count])
    return [str(i + 1) for i in range(count)]


def prompt_choice(prompt, valid_options, extras=()):
    """Ask until the answer is one of valid_options (or one of the extra typed commands, e.g. "SAVE")."""
    while True:
        choice = input(prompt).strip().upper()
        if choice in valid_options or choice in extras:
            return choice
        if len(valid_options) <= 8:
            valid_str = ", ".join(sorted(valid_options))
            print(f"  Please enter a valid option ({valid_str})!")
        else:
            print("  Please enter one of the listed options!")
