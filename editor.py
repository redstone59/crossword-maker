from typing import *
from enum import Enum

def clamp(value, lower, upper):
    return max(min(value, upper), lower)

class EditorModes(Enum):
    NORMAL  = 1 # Editing text
    FILL    = 2 # Editing bounds (symmetrical)
    FILTER  = 3 # Filtering dictionary results
    HINTS   = 4 # well
    REBUS   = 5 # Does not automatically shift square when typing
    PREVIEW = 6 # Removes all answers and places clue numbers on the board

class CrosswordEditor:
    def __init__(self, dictionaries: Dict[str, list[str]]):
        pass
    
    def main_loop(self):
        pass