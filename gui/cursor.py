from editor import clamp
from dataclasses import dataclass
from typing import *

def position_in_bounds(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return (0 <= a[0] < b[0]) and (0 <= a[1] < b[1])

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

    def shift_until(self, delta: int, condition: Callable[[int, int], bool]):
        while True:
            if self.going_down:
                self.row += delta
            else:
                self.column += delta
            
            if not (position_in_bounds(self.position(), self.edges) and condition(*self.position())):
                self.confine()
                break
    
    def change_position(self, delta_x, delta_y):
        self.row += delta_x
        self.column += delta_y
        self.confine()
    
    def position(self) -> tuple[int, int]:
        return self.row, self.column