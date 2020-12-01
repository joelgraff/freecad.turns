from typing import Final
from enum import Enum

class Enm(Enum):

    x = 1
    y = 2

class PickStyles():
    """
    SoPickStyle enumerants
    """

    UNPICKABLE: Final = 1
    SHAPE: Final = 2
    BOX: Final = 4
    SHAPE_ON_TOP: Final = 8
    BOX_ON_TOP: Final = 16
    FACES: Final = 32

    def __str__(self):

        return '__str()__'