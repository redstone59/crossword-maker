import regex as re
from typing import *

def create_filter(dictionaries: Dict[str, list[str]]) -> Callable[[str, str], Dict[str, list[str]]]:
    def find_all_words(pattern: str, replace_char: str = "*") -> Dict[str, list[str]]:
        all_results = {}
        
        for key in dictionaries:
            matches = dictionaries[key]
            matches = list(filter(lambda word: len(word) == len(pattern), matches))
            matches = list(filter(lambda word: re.match(pattern.replace(replace_char, r"\w"), word), matches))
            
            all_results[key] = matches
        
        return all_results
    
    return find_all_words