from typing import *
from copy import deepcopy
from dataclasses import dataclass

@dataclass
class SquareContents:
    character: str = " "
    colour: str = "white"
    filled: bool = False
    
    def __str__(self):
        return self.character

class Matrix:
    def __init__(self, rows: int, columns: int):
        self.contents = [[SquareContents()] * columns] * rows
        self.contents = [deepcopy([deepcopy(item) for item in row]) for row in self.contents]
        self.dimensions = (rows, columns)
    
    def deep_copy(self) -> Self:
        cloned_matrix = Matrix(*self.dimensions)
        cloned_matrix.contents = [deepcopy([deepcopy(item) for item in row]) for row in self.contents]
        return cloned_matrix
    
    def get_row(self, index: int):
        return self.contents[index]

    def get_column(self, index: int):
        return [row[index] for row in self.contents]
    
    def __getitem__(self, indices: tuple) -> SquareContents:
        row, column = indices
        return self.contents[row][column]
    
    def __setitem__(self, indices: tuple, value):
        row, column = indices
        self.contents[row][column] = value