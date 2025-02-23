from matrix import Matrix
from word_filter import create_filter
from editor import CrosswordEditor, EditorModes, clamp

from typing import *
from copy import deepcopy
from enum import Enum
import keyboard, os

class ConsoleEditor(CrosswordEditor):
    def __init__(self, dictionaries: Dict[str, list[str]]):
        self.find_all_words = create_filter(dictionaries)
        self.matrix = Matrix(int(input("Rows? ")), int(input("Columns? ")))
        self.cursor_pos = [0, 0]
        self.going_down = False
        self.mode = EditorModes.NORMAL
    
    def main_loop(self):
        self.display_matrix()
        while True:
            pressed = keyboard.read_event()
            
            if pressed.event_type != keyboard.KEY_DOWN: continue
            
            match pressed.name:
                case "left":
                    self.cursor_pos[1] -= 1
                case "right":
                    self.cursor_pos[1] += 1
                case "up":
                    self.cursor_pos[0] -= 1
                case "down":
                    self.cursor_pos[0] += 1
                case "esc":
                    break
                case "tab":
                    self.going_down = not self.going_down
                case _:
                    if len(pressed.name) == 1:
                        self.matrix[*self.cursor_pos] = pressed.name.lower()
                        if self.going_down:
                            self.cursor_pos[0] += 1
                        else:
                            self.cursor_pos[1] += 1
            
            self.cursor_pos[0] = clamp(self.cursor_pos[0], 0, self.matrix.dimensions[0] - 1)
            self.cursor_pos[1] = clamp(self.cursor_pos[1], 0, self.matrix.dimensions[1] - 1)
            
            self.display_matrix()
        
    def display_matrix(self):
        os.system("cls")
        display = [deepcopy(row) for row in self.matrix.contents]
        
        to_upper_char: str = display[self.cursor_pos[0]][self.cursor_pos[1]]
        display[self.cursor_pos[0]][self.cursor_pos[1]] = "^" if not to_upper_char.isalnum() else to_upper_char.upper()
        
        print("---\n" + "\n".join(["".join(row) for row in display]))