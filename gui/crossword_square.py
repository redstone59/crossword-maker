from dataclasses import dataclass
from matrix import Matrix, SquareContents
from app_theme import AppTheme

from typing import *
import pygame

@dataclass
class CrosswordSquare:
    surface: pygame.Surface
    position: pygame.Vector2
    size: int | float
    contents: SquareContents
    theme: AppTheme
    font: pygame.font.Font
    
    def new(surface: pygame.Surface, 
            position: pygame.Vector2, 
            size: int | float
            ) -> Self:
        return CrosswordSquare(surface, position, size)
    
    def draw(self) -> None:
        rect = pygame.Rect(self.position[0], self.position[1], self.size, self.size)
        pygame.draw.rect(self.surface,
                         self.theme.cw_fill if self.contents.filled else self.contents.colour,
                         rect,
                         )
        pygame.draw.rect(self.surface,
                         self.theme.cw_fill,
                         rect,
                         width = self.size // 30
                         )
        
        text = self.font.render(self.contents.character.upper(), False, "black")
        self.surface.blit(text,
                          text.get_rect(center = rect.center)
                          )

@dataclass
class RenderedMatrix:
    matrix: Matrix
    surface: pygame.Surface
    theme: AppTheme
    location: float = 0.5
    
    def draw(self):
        screen_rect = self.surface.get_rect()
        shortest_side = min(*screen_rect.size)
        longest_side = max(*screen_rect.size)
        
        square_size = shortest_side // self.matrix.dimensions[1]
        
        font_size = square_size * 8 // 10
        font = pygame.font.SysFont(self.theme.cw_font, font_size)
        
        starting_position = pygame.Vector2(int((longest_side - shortest_side) * self.location), 0)
        current_row = 0
        current_column = 0
        
        for row in self.matrix.contents:
            for square in row:
                position = starting_position + pygame.Vector2(current_column, current_row) * square_size
                CrosswordSquare(
                    self.surface,
                    position,
                    square_size,
                    square,
                    self.theme,
                    font
                ).draw()
                current_column += 1
            current_row += 1
            current_column = 0
        
        