# language/script_detect.py
import re

def detect_script(text: str) -> str:
    """
    Detects dominant script / language form.
    Returns:
    ENGLISH
    HINDI_SCRIPT
    TAMIL_SCRIPT
    ROMANIZED
    MIXED
    """

    has_devanagari = bool(re.search(r'[\u0900-\u097F]', text))
    has_tamil = bool(re.search(r'[\u0B80-\u0BFF]', text))
    has_latin = bool(re.search(r'[a-zA-Z]', text))

    if has_devanagari and not has_latin:
        return "HINDI_SCRIPT"

    if has_tamil and not has_latin:
        return "TAMIL_SCRIPT"

    if has_latin and not (has_devanagari or has_tamil):
        return "LATIN_ONLY"

    if has_latin and (has_devanagari or has_tamil):
        return "MIXED"

    return "UNKNOWN"
