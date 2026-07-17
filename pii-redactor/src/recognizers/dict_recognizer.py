import ahocorasick
from src.models import Entity
import json
from pathlib import Path

class DictionaryRecognizer:
    def __init__(self, dictionary_path: str, entity_label: str):
        self.entity_label = entity_label
        self.automaton = ahocorasick.Automaton()
        self.loaded = False
        
        path = Path(dictionary_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                words = json.load(f)
                for idx, word in enumerate(words):
                    self.automaton.add_word(word.lower(), (idx, word))
            self.automaton.make_automaton()
            self.loaded = True

    def detect(self, text: str, score: float = 0.8) -> list[Entity]:
        if not self.loaded:
            return []
            
        entities = []
        lower_text = text.lower()
        for end_idx, (idx, original_word) in self.automaton.iter(lower_text):
            start_idx = end_idx - len(original_word) + 1
            
            # Ensure it's a word boundary match to avoid substring false positives
            if start_idx > 0 and lower_text[start_idx-1].isalnum():
                continue
            if end_idx < len(lower_text) - 1 and lower_text[end_idx+1].isalnum():
                continue
                
            entities.append(Entity(
                text=text[start_idx:end_idx+1],
                label=self.entity_label,
                start=start_idx,
                end=end_idx+1,
                score=score,
                source="dictionary"
            ))
        return entities
