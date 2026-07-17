import spacy
from src.models import Entity

try:
    nlp = spacy.load("en_core_web_lg")
except OSError:
    print("Warning: spacy model 'en_core_web_lg' not found. Please install it.")
    nlp = None

ORG_BOOST_CONTEXTS = [
    "limited", "ltd", "pvt", "private", "inc", "corp",
    "llp", "trust", "foundation", "holdings", "ventures",
    "family trust", "associates", "group", "solutions", "technologies"
]

def boost_org_score(entity: Entity, surrounding_text: str) -> Entity:
    lower = surrounding_text.lower()
    for keyword in ORG_BOOST_CONTEXTS:
        if keyword in lower:
            entity.score = min(entity.score + 0.15, 1.0)
            break
    return entity

def detect_orgs(text: str) -> list[Entity]:
    if not nlp:
        return []
        
    doc = nlp(text)
    entities = []
    
    # We create a simple context window around the entity for boosting
    for ent in doc.ents:
        if ent.label_ == "ORG":
            start_context = max(0, ent.start_char - 50)
            end_context = min(len(text), ent.end_char + 50)
            context = text[start_context:end_context]
            
            entity = Entity(
                text=ent.text, 
                label="ORGANIZATION",
                start=ent.start_char, 
                end=ent.end_char,
                score=0.75, 
                source="spacy_ner"
            )
            entity = boost_org_score(entity, context)
            entities.append(entity)
        elif ent.label_ in ("GPE", "LOC", "FAC"):
            entity = Entity(
                text=ent.text, 
                label="LOCATION",
                start=ent.start_char, 
                end=ent.end_char,
                score=0.85, # High score to override false positive organizations
                source="spacy_ner"
            )
            entities.append(entity)
            
    return entities
