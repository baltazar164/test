def search4letters(phrase:str, lettets:str = 'aeiou') -> set:
    return set(lettets).intersection(set(phrase))
