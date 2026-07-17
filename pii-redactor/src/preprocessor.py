import unicodedata
import re
from src.models import TextSpan
from src.structural_context import normalize_caps

def preprocess(spans: list[TextSpan]) -> tuple[str, list[tuple[int, int, TextSpan]]]:
    # Joins text while keeping a mapping back to spans
    # This is a complex operation; for simplicity in this MVP, we will yield a single string
    # and a mapping of character offsets to the originating span.
    
    full_text = ""
    mapping = [] # list of (start, end, TextSpan)
    
    for span in spans:
        start = len(full_text)
        # normalize unicode
        text = unicodedata.normalize("NFKC", span.text)
        full_text += text
        end = len(full_text)
        mapping.append((start, end, span))
        
    # wrapped word joining would adjust full_text and the mapping.
    # We will just do ALL-CAPS title-casing on the full text.
    normalized_full_text = normalize_caps(full_text)
    
    return normalized_full_text, mapping
