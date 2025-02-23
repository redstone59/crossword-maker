import regex as re
from collections.abc import Callable

def create_filter(dictionaries: dict[str, list[str]]) -> Callable[[str, str], dict[str, list[str]]]:
    def find_all_words(pattern: str, replace_char: str = "*") -> dict[str, list[str]]:
        all_results = {}
        
        for key in dictionaries:
            matches = dictionaries[key]
            matches = list(filter(lambda word: len(word) == len(pattern), matches))
            matches = list(filter(lambda word: re.match(pattern.replace(replace_char, r"\w"), word), matches))
            
            all_results[key] = matches
        
        return all_results
    
    return find_all_words