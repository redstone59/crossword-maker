from editor import CrosswordEditor, EditorModes
from matrix import Matrix, SquareContents
from word_filter import create_filter
from gui.crossword_square import RenderedMatrix
from gui.app_theme import AppTheme
from gui.cursor import Cursor

from typing import *
from dataclasses import dataclass
import pygame

FILL_MODES = [EditorModes.FILL, EditorModes.FILL_ASYMMETRICAL]
TYPING_MODES = [EditorModes.NORMAL, EditorModes.REBUS, EditorModes.HINTS, EditorModes.FILTER]

def get_all_points(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    x_bounds = (a[0], b[0] + 1) if a[0] <= b[0] else (b[0], a[0] + 1)
    y_bounds = (a[1], b[1] + 1) if a[1] <= b[1] else (b[1], a[1] + 1)
    
    all_points = []
    
    for points in [[(row, column) for column in range(*y_bounds)] for row in range(*x_bounds)]:
        all_points += points
    
    return all_points

def mirror(position: tuple[int, int], edges: tuple[int, int]) -> tuple[int, int]:
    return (edges[0] - position[0] - 1, edges[1] - position[1] - 1)

def isolate_word(index: int, squares: list[SquareContents]) -> list[SquareContents]:
    end = None
    for offset in range(len(squares) - index):
        if not squares[index + offset].filled:
            continue
        
        end = index + offset
        break
    
    if end == None:
        end = len(squares)
    
    start = None
    for offset in range(index):
        if not squares[index - offset - 1].filled:
            continue
        
        start = index - offset
        break
    
    if start == None:
        start = 0
    
    return squares[start:end]

def find_cursor_words(matrix: Matrix, position: tuple[int, int]) -> tuple[str, str]:
    if matrix[*position].filled: return "", ""
    
    row, column = matrix.get_row(position[0]), matrix.get_column(position[1])
    row_string = "".join([square.character for square in isolate_word(position[1], row)])
    column_string = "".join([square.character for square in isolate_word(position[0], column)])
    
    return row_string, column_string

@dataclass
class PreviousWord:
    string: str = ""
    results: Dict[str, list[str]] = {}

class PygameGUI(CrosswordEditor):
    def __init__(self, dictionaries: Dict[str, list[str]]):
        self.theme = AppTheme()
        
        self.find_all_words = create_filter(dictionaries)
        self.matrix = Matrix(11, 11, self.theme.cw_background)
        self.cursor = Cursor(edges = self.matrix.dimensions)
        self.mode: EditorModes = EditorModes.NORMAL
        self.start_select: tuple[int, int] = (0, 0)
        
        self.needs_refresh: bool = False
        self.previous_across = PreviousWord()
        self.previous_down = PreviousWord()
        
        
        pygame.init()
        pygame.key.start_text_input()
        self.screen = pygame.display.set_mode((1920, 1080))
        self.clock = pygame.time.Clock()
        self.running = True
        self.matrix_position = 0 # The crossword renders on the left hand side of the window.
    
    def main_loop(self):
        while self.running:
            self.handle_events()
            if self.needs_refresh:
                self.refresh_words()
                self.needs_refresh = False
            self.render_all()
            self.clock.tick(60)
        
        pygame.key.stop_text_input()
        pygame.quit()
    
    def delete_selection(self):
        for index in get_all_points(self.start_select, self.cursor.position()):
            self.matrix[*index].character = " "
    
    def fill_until_edge(self, to_highlight: Matrix, delta: int):
        current_cursor_position = self.cursor.position()
        
        while True:
            to_highlight[*self.cursor.position()].colour = self.theme.highlight
            if not self.cursor.shift_if(delta, lambda x, y: not to_highlight[x, y].filled):
                break
        
        self.cursor.row, self.cursor.column = current_cursor_position
    
    def refresh_words(self):
        across_string, down_string = find_cursor_words(self.matrix, self.cursor.position())
        
        waste_of_time = lambda word: len(word) < 3 or word.isspace() or word.count(" ") >= 5
        
        if self.previous_across.string != across_string:
            across_words = {} if waste_of_time(across_string) else self.find_all_words(across_string, " ")
            self.previous_across = PreviousWord(across_string, across_words)
        else:
            across_words = self.previous_across.results
        
        if self.previous_down.string != down_string:
            down_words = {} if waste_of_time(down_string) else self.find_all_words(down_string, " ")
            self.previous_down = PreviousWord(down_string, down_words)
        else:
            down_words = self.previous_down.results
        
        print(across_words)
        
    
    def handle_events(self):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                case pygame.KEYDOWN:
                    self.handle_key(event)
    
    def handle_key(self, event: pygame.event.Event):
        can_type = self.mode in [EditorModes.NORMAL, EditorModes.REBUS]
        typed_letter = event.dict["unicode"].isalnum()
        ctrl_pressed = event.dict["mod"] & pygame.KMOD_CTRL > 0

        in_normal_mode = self.mode == EditorModes.NORMAL
        
        square_not_filled = lambda x, y: not self.matrix[x, y].filled
        
        if can_type and not ctrl_pressed and typed_letter:
            if in_normal_mode:
                self.matrix[*self.cursor.position()].character = event.dict["unicode"]
                self.cursor.shift_if(1, square_not_filled)
            else:
                if self.matrix[*self.cursor.position()].character.isspace():
                    self.matrix[*self.cursor.position()].character = ""
                    
                self.matrix[*self.cursor.position()].character += event.dict["unicode"]
                
            self.needs_refresh = True
            return

        if ctrl_pressed:
            self.handle_ctrl_keys(event)
            return

        if event.dict["unicode"] == "#":
            self.mode = EditorModes.FILL
            return

        match event.dict["key"]:
            case pygame.K_ESCAPE:
                if not in_normal_mode:
                    self.mode = EditorModes.NORMAL
                    
            # Switching modes
            
            case pygame.K_F1:
                self.start_select = self.cursor.position()
                self.mode = EditorModes.SELECT
            case pygame.K_F2:
                self.mode = EditorModes.FILL
            case pygame.K_F3:
                self.mode = EditorModes.HINTS
            case pygame.K_F4:
                self.mode = EditorModes.PREVIEW
                
            # Removing text
            
            case pygame.K_BACKSPACE:
                if self.mode == EditorModes.SELECT:
                    self.delete_selection()
                    return
                
                if self.matrix[*self.cursor.position()].character.isspace():
                    self.cursor.shift_if(-1, square_not_filled)
                
                has_multiple_characters = len(self.matrix[*self.cursor.position()].character) > 1
                if has_multiple_characters:
                    self.matrix[*self.cursor.position()].character = self.matrix[*self.cursor.position()].character[:-1]
                else:
                    self.matrix[*self.cursor.position()].character = " "
            
            case pygame.K_DELETE:
                if self.mode == EditorModes.SELECT:
                    self.delete_selection()
                    return
                
                self.matrix[*self.cursor.position()].character = " "
                
            # Movement
            
            case pygame.K_TAB:
                self.cursor.going_down = not self.cursor.going_down
            case pygame.K_f:
                if self.mode == EditorModes.FILL:
                    self.cursor.row, self.cursor.column = mirror(self.cursor.position(), self.matrix.dimensions)
            
            case pygame.K_UP:
                if in_normal_mode:
                    self.cursor.going_down = True
                    self.cursor.shift_until(-1, square_not_filled)
                else:
                    self.cursor.change_position(-1, 0)
                
                self.needs_refresh = True
                    
            case pygame.K_DOWN:
                if in_normal_mode:
                    self.cursor.going_down = True
                    self.cursor.shift_until(1, square_not_filled)
                else:
                    self.cursor.change_position(1, 0)
                
                self.needs_refresh = True
                    
            case pygame.K_LEFT:
                if in_normal_mode:
                    self.cursor.going_down = False
                    self.cursor.shift_until(-1, square_not_filled)
                else:
                    self.cursor.change_position(0, -1)
                
                self.needs_refresh = True
                    
            case pygame.K_RIGHT:
                if in_normal_mode:
                    self.cursor.going_down = False
                    self.cursor.shift_until(1, square_not_filled)
                else:
                    self.cursor.change_position(0, 1)
                
                self.needs_refresh = True
            
            # Filling in squares
            
            case pygame.K_SPACE | pygame.K_RETURN:
                if self.mode in FILL_MODES:
                    self.matrix[*self.cursor.position()].filled = not self.matrix[*self.cursor.position()].filled
                if self.mode == EditorModes.FILL:
                    mirrored_position = mirror(self.cursor.position(), self.matrix.dimensions)
                    if mirrored_position == self.cursor.position(): return
                    self.matrix[*mirrored_position].filled = not self.matrix[*mirrored_position].filled
                    return
                
                if self.mode in TYPING_MODES:
                    print("TODO: toggle between hints (like hitting tab on nyt)")
            
            # Fallthrough
            
            case _:
                print("Unknown key: " + str(event.dict))
    
    def handle_ctrl_keys(self, event: pygame.event.Event):
        square_not_filled = lambda x, y: not self.matrix[x, y].filled
        square_is_filled = lambda x, y: self.matrix[x, y].filled
        
        match event.dict["key"]:
            # Common shortcuts

            case pygame.K_c:
                pass
            case pygame.K_x:
                pass
            case pygame.K_v:
                pass
            case pygame.K_w:
                self.running = False
                
            # Changing modes
            
            case pygame.K_F2:
                self.mode = EditorModes.FILL_ASYMMETRICAL
            case pygame.K_r:
                self.mode = EditorModes.REBUS
            case pygame.K_f:
                self.mode = EditorModes.FILTER
            case pygame.K_v:
                self.mode = EditorModes.SELECT
            
            # File options
            
            case pygame.K_s:
                print("TODO: save crossword here")
            case pygame.K_e:
                print("TODO: implement exporters")
                
            # Faster moving
            
            case pygame.K_UP:
                self.cursor.going_down = True
                if self.cursor.check(-1, square_is_filled):
                    self.cursor.shift_until(-1, square_not_filled)
                else:
                    self.cursor.shift_until(-1, square_is_filled, False)
                
                if self.matrix[*self.cursor.position()].filled:
                    # Place cursor outside of filled square.
                    self.cursor.shift(1)
                
                self.needs_refresh = True
            
            case pygame.K_DOWN:
                self.cursor.going_down = True
                if self.cursor.check(1, square_is_filled):
                    self.cursor.shift_until(1, square_not_filled)
                else:
                    self.cursor.shift_until(1, square_is_filled, False)
                
                if self.matrix[*self.cursor.position()].filled:
                    # Place cursor outside of filled square.
                    self.cursor.shift(-1)
                
                self.needs_refresh = True
            
            case pygame.K_LEFT:
                self.cursor.going_down = False
                if self.cursor.check(-1, square_is_filled):
                    self.cursor.shift_until(-1, square_not_filled)
                else:
                    self.cursor.shift_until(-1, square_is_filled, False)
                
                if self.matrix[*self.cursor.position()].filled:
                    # Place cursor outside of filled square.
                    self.cursor.shift(1)
                
                self.needs_refresh = True
            
            case pygame.K_RIGHT:
                self.cursor.going_down = False
                if self.cursor.check(1, square_is_filled):
                    self.cursor.shift_until(1, square_not_filled)
                else:
                    self.cursor.shift_until(1, square_is_filled, False)
                
                if self.matrix[*self.cursor.position()].filled:
                    # Place cursor outside of filled square.
                    self.cursor.shift(-1)
                
                self.needs_refresh = True
            
            # Fallthrough
            
            case _:
                print("Unknown key: " + str(event.dict))
    
    def highlight_matrix(self) -> Matrix:
        highlight = self.matrix.deep_copy()
        
        match self.mode:
            case EditorModes.NORMAL | EditorModes.REBUS | EditorModes.HINTS | EditorModes.FILTER:
                if not self.matrix[*self.cursor.position()].filled:
                    self.fill_until_edge(highlight, 1)
                    self.fill_until_edge(highlight, -1)
            case EditorModes.FILL:
                mirrored_position = mirror(self.cursor.position(), self.matrix.dimensions)
                highlight[*mirrored_position].colour = self.theme.highlight
                highlight[*mirrored_position].selected = True
            case EditorModes.SELECT:
                selected_region = get_all_points(self.start_select, self.cursor.position())
                for index in selected_region:
                    highlight[*index].colour = self.theme.highlight
                    highlight[*index].selected = True
        
        if self.mode not in [EditorModes.PREVIEW, EditorModes.HINTS]:
            highlight[*self.cursor.position()].colour = self.theme.cursor_colour
            highlight[*self.cursor.position()].selected = True
        
        return highlight
    
    def render_all(self):
        self.screen.fill(self.theme.app_background) # Remove anything on buffer

        self.render_crossword()
        self.render_words()
    
        pygame.display.flip()
    
    def render_crossword(self):
        highlighted_matrix = self.highlight_matrix()
        RenderedMatrix(highlighted_matrix, self.screen, self.theme, self.matrix_position).draw()

    def render_words(self):
        pass

    def update_dimensions(self, new_rows: int, new_columns: int):
        self.matrix = Matrix(new_rows, new_columns)
        self.cursor.edges = (new_rows, new_columns)