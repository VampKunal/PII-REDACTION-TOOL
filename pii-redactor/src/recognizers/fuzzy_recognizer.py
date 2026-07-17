from rapidfuzz import process, fuzz
from src.models import Entity
import json
from pathlib import Path
import re

class FuzzyRecognizer:
    def __init__(self, dictionary_path: str, entity_label: str, threshold: float = 85.0):
        self.entity_label = entity_label
        self.threshold = threshold
        self.words = []
        
        path = Path(dictionary_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                self.words = json.load(f)

    def detect(self, text: str) -> list[Entity]:
        if not self.words:
            return []
            
        entities = []
        # A simple approach: we extract capitalized n-grams (1 to 4 words) 
        # from the text to test against the fuzzy dictionary.
        # Running fuzzy matching on every single word is too slow and inaccurate.
        
        # Find sequences of capitalized words
        pattern = re.compile(r'([A-Z][a-z0-9]+\s?)+')
        for match in pattern.finditer(text):
            candidate = match.group().strip()
            if len(candidate) < 4:
                continue
                
            # Use fuzz.token_sort_ratio for comparison
            result = process.extractOne(candidate, self.words, scorer=fuzz.token_sort_ratio)
            if result:
                best_match, score, _ = result
                if score >= self.threshold:
                    entities.append(Entity(
                        text=candidate,
                        label=self.entity_label,
                        start=match.start(),
                        end=match.start() + len(candidate),
                        score=min(score / 100.0, 1.0),
                        source="fuzzy"
                    ))
        return entities
