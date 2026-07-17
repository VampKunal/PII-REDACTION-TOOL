from src.mapping_store import MappingStore
from src.models import Entity

REPLACEMENT_GENERATORS = {
    "PERSON":        lambda: "<PERSON>",
    "EMAIL":         lambda: "<EMAIL>",
    "PHONE_NUMBER":  lambda: "<PHONE_NUMBER>",
    "ORGANIZATION":  lambda: "<ORGANIZATION>",
    "ADDRESS":       lambda: "<ADDRESS>",
    "US_SSN":        lambda: "<US_SSN>",
    "CREDIT_CARD":   lambda: "<CREDIT_CARD>",
    "DATE_OF_BIRTH": lambda: "<DATE_OF_BIRTH>",
    "IP_ADDRESS":    lambda: "<IP_ADDRESS>",
    "LOCATION":      lambda: "<LOCATION>",
    # fallback
    "DEFAULT":       lambda: "***REDACTED***"
}

def replace_entities(entities: list[Entity], text: str, mapping: MappingStore) -> list[tuple[Entity, str, str]]:
    # Returns list of (Entity, Original, Replacement)
    replacements = []
    for ent in entities:
        original = text[ent.start:ent.end]
        generator = REPLACEMENT_GENERATORS.get(ent.label, REPLACEMENT_GENERATORS["DEFAULT"])
        replacement = mapping.get_replacement(ent.label, original, generator)
        replacements.append((ent, original, replacement))
    return replacements

def apply_replacements_to_spans(spans, replacements):
    # Sort replacements by start length (longest first to avoid substring bugs)
    replacements.sort(key=lambda x: len(x[1]), reverse=True)
    
    for span in spans:
        # First, apply forced labels from structural context
        if getattr(span, "forced_label", None):
            generator = REPLACEMENT_GENERATORS.get(span.forced_label, REPLACEMENT_GENERATORS["DEFAULT"])
            span.text = generator()
            span.run_ref.text = span.text
            continue # Skip substring replacements if the whole span is forced
            
        for ent, original, replacement in replacements:
            if original in span.text:
                span.text = span.text.replace(original, replacement)
                span.run_ref.text = span.text
