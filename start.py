import os, sys, pathlib

DICTIONARIES_PATH = pathlib.Path(os.path.dirname(os.path.abspath(sys.argv[0])), "dictionaries")
ALL_DICTIONARIES = {}
with os.scandir(DICTIONARIES_PATH) as entries:
    for entry in entries:
        if not entry.is_file: continue
        
        with open(pathlib.Path(DICTIONARIES_PATH, entry.name)) as file:
            ALL_DICTIONARIES[entry.name] = file.read().split("\n")

no_gui = False

if no_gui:
    from editor import CrosswordEditor
    CrosswordEditor(ALL_DICTIONARIES).main_loop()
else:
    from gui.pygame_gui import PygameGUI
    PygameGUI(ALL_DICTIONARIES).main_loop()