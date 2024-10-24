from editor import CrosswordEditor
from dataclasses import dataclass

# File extension, description
# i.e. ("*.png", "PNG image file") or (".docx", "Microsoft Word document")
FileType = tuple[str, str]

@dataclass
class Exporter:
    name: str                           # 
    creator: str | list[str]            # Contributor(s) to creation
    exports: FileType | list[FileType]  # The formats that a crossword could be exported to
    settings: dict[str, type]           # Additional settings (like size, image quality, etc.) that can be inputted
    
    def export(self, editor: CrosswordEditor, name: str) -> bool:
        pass