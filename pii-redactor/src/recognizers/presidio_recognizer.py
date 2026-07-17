from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from src.models import Entity

configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

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
