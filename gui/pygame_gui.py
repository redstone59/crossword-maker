from editor import CrosswordEditor, EditorModes, clamp
from matrix import Matrix, SquareContents
from gui.crossword_square import RenderedMatrix
from gui.app_theme import AppTheme
from gui.cursor import Cursor

from typing import *
import pygame

def mirror(position: tuple[int, int], edges: tuple[int, int]) -> tuple[int, int]:
    return (edges[0] - position[0] - 1, edges[1] - position[1] - 1)

class PygameGUI(CrosswordEditor):
    def __init__(self, dictionaries: Dict[str, list[str]]):
        self.dictionaries = dictionaries
        self.matrix = Matrix(12, 12)
        self.cursor = Cursor(edges = self.matrix.dimensions)
        self.mode: EditorModes = EditorModes.NORMAL
        
        pygame.init()
        pygame.key.start_text_input()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.running = True
        self.matrix_position = 0.5
        
        self.theme = AppTheme()
    
    def main_loop(self):
        while self.running:
            self.handle_events()
            self.render_graphics()
            self.clock.tick(60)
        
        pygame.key.stop_text_input()
        pygame.quit()
    
    def fill_until_edge(self, to_highlight: Matrix, delta: int):
        current_cursor_position = self.cursor.position()
        
        while True:
            to_highlight[*self.cursor.position()].colour = self.theme.highlight
            if not self.cursor.shift_if(delta, lambda x, y: not to_highlight[x, y].filled):
                break
        
        self.cursor.row, self.cursor.column = current_cursor_position
            
    def handle_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    self.handle_key(event)
    
    def handle_key(self, event: pygame.event.Event):
        in_normal_mode = self.mode == EditorModes.NORMAL
        typed_letter = event.dict["unicode"].isalnum()
        ctrl_pressed = event.dict["mod"] & pygame.KMOD_CTRL > 0
        
        square_not_filled = lambda x, y: not self.matrix[x, y].filled
        square_is_filled = lambda x, y: self.matrix[x, y].filled
        
        if in_normal_mode and not ctrl_pressed and typed_letter:
            self.matrix[*self.cursor.position()].character = event.dict["unicode"]
            self.cursor.shift_if(1, square_not_filled)
            return

        if ctrl_pressed:
            self.handle_ctrl_keys(event)
            return

        if event.dict["unicode"] == "#":
            self.mode = EditorModes.FILL

        match event.dict["key"]:
            case pygame.K_ESCAPE:
                if not in_normal_mode:
                    self.mode = EditorModes.NORMAL
                    
            # Switching modes
            
            case pygame.K_F1:
                self.mode = EditorModes.SELECT
            case pygame.K_F2:
                self.mode = EditorModes.FILL
            case pygame.K_F3:
                self.mode = EditorModes.HINTS
            case pygame.K_F4:
                self.mode = EditorModes.PREVIEW
                
            # Removing text
            
            case pygame.K_BACKSPACE:
                if self.matrix[*self.cursor.position()].character.isspace():
                    self.cursor.shift_if(-1, square_not_filled)
                self.matrix[*self.cursor.position()].character = " "
            case pygame.K_DELETE:
                self.matrix[*self.cursor.position()].character = " "
            case pygame.K_TAB:
                self.cursor.going_down = not self.cursor.going_down
                
            # Movement
            
            case pygame.K_UP:
                if in_normal_mode:
                    self.cursor.going_down = True
                    self.cursor.shift_until(-1, square_is_filled)
                else:
                    self.cursor.change_position(-1, 0)
            case pygame.K_DOWN:
                if in_normal_mode:
                    self.cursor.going_down = True
                    self.cursor.shift_until(1, square_is_filled)
                else:
                    self.cursor.change_position(1, 0)
            case pygame.K_LEFT:
                if in_normal_mode:
                    self.cursor.going_down = False
                    self.cursor.shift_until(-1, square_is_filled)
                else:
                    self.cursor.change_position(0, -1)
            case pygame.K_RIGHT:
                if in_normal_mode:
                    self.cursor.going_down = False
                    self.cursor.shift_until(1, square_is_filled)
                else:
                    self.cursor.change_position(0, 1)
            
            # Filling in squares
            
            case pygame.K_SPACE | pygame.K_RETURN:
                if self.mode in [EditorModes.FILL, EditorModes.FILL_ASYMMETRICAL]:
                    self.matrix[*self.cursor.position()].filled = not self.matrix[*self.cursor.position()].filled
                if self.mode == EditorModes.FILL:
                    mirrored_position = mirror(self.cursor.position(), self.matrix.dimensions)
                    self.matrix[*mirrored_position].filled = not self.matrix[*mirrored_position].filled
            
            # Fallthrough
            
            case _:
                print("Unknown key: " + str(event.dict))
    
    def handle_ctrl_keys(self, event: pygame.event.Event):
        if event.dict["unicode"] == "":
            return
        
        match event.dict["key"]:
            case pygame.K_q:
                self.matrix_position -= 0.5
                self.matrix_position = clamp(self.matrix_position, 0, 1)
            case pygame.K_w:
                self.matrix_position += 0.5
                self.matrix_position = clamp(self.matrix_position, 0, 1)
            case pygame.K_r:
                self.mode = EditorModes.REBUS
            case pygame.K_f:
                self.mode = EditorModes.FILTER
            case pygame.K_v:
                self.mode = EditorModes.SELECT
            case pygame.K_s:
                print("TODO: save crossword here")
            case pygame.K_e:
                print("TODO: implement exporters")
            case _:
                print("Unknown key: " + str(event.dict))
    
    def highlight_words(self) -> Matrix:
        highlight = self.matrix.deep_copy()
        
        not_editing_board = self.mode in [EditorModes.NORMAL, EditorModes.HINTS, EditorModes.FILTER]
        if not_editing_board:
            self.fill_until_edge(highlight, 1)
            self.fill_until_edge(highlight, -1)
        elif self.mode == EditorModes.FILL:
            mirrored_position = mirror(self.cursor.position(), self.matrix.dimensions)
            highlight[*mirrored_position].colour = self.theme.highlight
        highlight[*self.cursor.position()].colour = self.theme.cursor_colour
        
        return highlight
    
    def render_graphics(self):
        self.screen.fill(self.theme.app_background) # Remove anything on buffer
        
        highlighted_matrix = self.highlight_words()
        
        RenderedMatrix(highlighted_matrix, self.screen, self.theme.cw_font, self.matrix_position).draw()
        
        pygame.display.flip()

    def update_dimensions(self, new_rows: int, new_columns: int):
        self.matrix = Matrix(new_rows, new_columns)
        self.cursor.edges = (new_rows, new_columns)