from fuzzywuzzy import fuzz

FUZZY_MATCH_THRESHOLD = 60


def fuzzySusDetector(string: str, comparision: str) -> bool:
    if fuzz.ratio(string.lower(), comparision) > FUZZY_MATCH_THRESHOLD:
        return True
    return False
