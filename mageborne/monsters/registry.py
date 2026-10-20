from .goblin import Goblin
from .archer import Archer
from .fairy import Fairy
from .skeleton import Skeleton
from .dragon import Dragon
from .snake import Snake
from .troll import Troll
from .witch import Witch

# Name used in encounter dicts -> monster class
MONSTER_TYPES = {
    "goblin":   Goblin,
    "archer":   Archer,
    "fairy":    Fairy,
    "skeleton": Skeleton,
    "dragon":   Dragon,
    "snake":    Snake,
    "troll":    Troll,
    "witch":    Witch,
}
