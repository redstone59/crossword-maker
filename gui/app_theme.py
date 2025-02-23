from dataclasses import dataclass

Colour = tuple[int, int, int]

@dataclass
class AppTheme:
    # Crossword default colours (exported)
    cw_background: Colour = (255, 255, 255)
    cw_text: Colour = (0, 0, 0)
    cw_accent: Colour = (200, 200, 200) # For pointing out extra messages
    cw_fill: Colour = (0, 0, 0)
    cw_font: str = "arial"
    
    # Other visual elements
    app_background: Colour = (70, 70, 80)
    cursor_colour: Colour = (255, 218, 0)
    highlight: Colour = (167, 216, 255)