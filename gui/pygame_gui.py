from editor import CrosswordEditor, EditorModes, clamp
from matrix import Matrix, SquareContents
from gui.crossword_square import RenderedMatrix

from typing import *
from dataclasses import dataclass

import pygame

@dataclass
class Cursor:
    row: int = 0
    column: int = 0
    edges: tuple[int, int] = (0, 0)
    going_down: bool = False
    
    def confine(self):
        self.row = clamp(self.row, 0, self.edges[0] - 1)
        self.column = clamp(self.column, 0, self.edges[1] - 1)
        
    def shift(self, delta: int):
        if self.going_down:
            self.row += delta
        else:
            self.column += delta
            
        self.confine()
    
    def shift_if(self, delta: int, condition: Callable[[int, int], bool]):
        if self.going_down:
            next_position = (self.row + delta, self.column)
        else:
            next_position = (self.row, self.column + delta)
        
        if next_position[0] >= self.edges[0] or next_position[1] >= self.edges[1]:
            return
        
        if condition(*next_position):
            self.shift(delta)
    
    def change_position(self, delta_x, delta_y):
        self.row += delta_x
        self.column += delta_y
        self.confine()
    
    def position(self) -> tuple[int, int]:
        return self.row, self.column

class PygameGUI(CrosswordEditor):
    def __init__(self, dictionaries: Dict[str, list[str]]):
        self.dictionaries = dictionaries
        self.matrix = Matrix(5, 5)
        self.cursor = Cursor(edges = self.matrix.dimensions)
        self.mode: EditorModes = EditorModes.NORMAL
        
        pygame.init()
        pygame.key.start_text_input()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.font = "arial"
    
    def main_loop(self):
        while self.running:
            self.handle_events()
            self.render_graphics()
            self.clock.tick(60)
        
        pygame.key.stop_text_input()
        pygame.quit()
    
    def handle_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    self.handle_key(event)
    
    def handle_key(self, event: pygame.event.Event):
        if self.mode == EditorModes.NORMAL and event.dict["unicode"].isalnum():
            self.matrix[*self.cursor.position()].character = event.dict["unicode"]
            self.cursor.shift_if(1, lambda x, y: not self.matrix[x, y].filled)
            return

        if event.dict["unicode"] == "#": # temporary measure
            self.matrix[*self.cursor.position()].filled = not self.matrix[*self.cursor.position()].filled

        match event.dict["key"]:
            case pygame.K_BACKSPACE:
                if self.matrix[*self.cursor.position()].character.isspace():
                    self.cursor.shift(-1)
                self.matrix[*self.cursor.position()].character = " "
            case pygame.K_DELETE:
                self.matrix[*self.cursor.position()].character = " "
            case pygame.K_TAB:
                self.cursor.going_down = not self.cursor.going_down
            case pygame.K_UP:
                self.cursor.change_position(-1, 0)
            case pygame.K_DOWN:
                self.cursor.change_position(1, 0)
            case pygame.K_LEFT:
                self.cursor.change_position(0, -1)
            case pygame.K_RIGHT:
                self.cursor.change_position(0, 1)
            case _:
                print("Unknown key: " + str(event.dict))
    
    def render_graphics(self):
        self.screen.fill((70, 70, 80)) # Remove anything on buffer
        
        previous_colour = self.matrix[*self.cursor.position()].colour
        self.matrix[*self.cursor.position()].colour = (180, 180, 180)
        
        RenderedMatrix(self.matrix, self.screen, self.font).draw()
        
        self.matrix[*self.cursor.position()].colour = previous_colour
        
        pygame.display.flip()

    def update_dimensions(self, new_rows: int, new_columns: int):
        self.matrix = Matrix(new_rows, new_columns)
        self.cursor.edges = (new_rows, new_columns)