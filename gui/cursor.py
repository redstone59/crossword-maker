from editor import clamp
from dataclasses import dataclass
from collections.abc import Callable

def position_in_bounds(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return (0 <= a[0] < b[0]) and (0 <= a[1] < b[1])

@dataclass
class Cursor:
    row: int = 0
    column: int = 0
    edges: tuple[int, int] = (0, 0)
    going_down: bool = False
    
    def _shift(self, delta):
        if self.going_down:
            self.row += delta
        else:
            self.column += delta
    
    def confine(self):
        self.row = clamp(self.row, 0, self.edges[0] - 1)
        self.column = clamp(self.column, 0, self.edges[1] - 1)
    
    def change_position(self, delta_x, delta_y):
        self.row += delta_x
        self.column += delta_y
        self.confine()
    
    def check(self, delta: int, func: Callable[[int, int], bool]) -> bool:
        self._shift(delta)
        
        if position_in_bounds(self.position(), self.edges):
            result = func(*self.position())
        else:
            result = False
        
        self._shift(-delta)
        return result
    
    def position(self) -> tuple[int, int]:
        return self.row, self.column
        
    def shift(self, delta: int):
        self._shift(delta)
        self.confine()
    
    def shift_if(self, delta: int, condition: Callable[[int, int], bool]) -> bool:
        if self.going_down:
            next_position = (self.row + delta, self.column)
        else:
            next_position = (self.row, self.column + delta)
        
        if not position_in_bounds(next_position, self.edges):
            return False
        
        if condition(*next_position):
            self.shift(delta)
            return True

        return False

    def shift_until(self, delta: int, condition: Callable[[int, int], bool], revert_on_edge = True):
        last_valid_square = self.position()
        while True:
            self._shift(delta)
            
            if not position_in_bounds(self.position(), self.edges):
                if revert_on_edge:
                    self.row, self.column = last_valid_square
                else:
                    self._shift(-delta)
                break
            
            if condition(*self.position()):
                self.confine()
                break