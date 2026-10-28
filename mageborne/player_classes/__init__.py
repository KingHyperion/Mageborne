from .warrior import Warrior
from .mage import Mage
from .thief import Thief

# Class name -> class. Mods add their own entries at startup (see mod_loader.py),
# and the class menu in main.py is built from this dict automatically.
PLAYER_CLASSES = {cls.class_name: cls for cls in (Warrior, Mage, Thief)}
