from .warrior import Warrior
from .mage import Mage
from .thief import Thief

# Menu key -> class. Add a new class here and it shows up in the menu.
PLAYER_CLASSES = {
    "A": Warrior,
    "B": Mage,
    "C": Thief,
}
