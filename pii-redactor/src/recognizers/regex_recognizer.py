import re
from src.models import Entity

class RegexRecognizer:
    def __init__(self, pattern: str, entity_label: str, score: float = 0.5):
        self.pattern = re.compile(pattern)
        self.entity_label = entity_label
        self.score = score

    def detect(self, text: str) -> list[Entity]:
        entities = []
        for match in self.pattern.finditer(text):
            entities.append(Entity(
                text=match.group(0),
                label=self.entity_label,
                start=match.start(),
                end=match.end(),
                score=self.score,
                source="regex"
            ))
        return entities
