from presidio_analyzer import AnalyzerEngine
from src.models import Entity

analyzer = AnalyzerEngine()

def detect_presidio(text: str, score_threshold: float = 0.5) -> list[Entity]:
    results = analyzer.analyze(text=text, language="en", score_threshold=score_threshold)
    
    entities = []
    for r in results:
        entities.append(Entity(
            text=text[r.start:r.end],
            label=r.entity_type,
            start=r.start,
            end=r.end,
            score=r.score,
            source="presidio"
        ))
    return entities
