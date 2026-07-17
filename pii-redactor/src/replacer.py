from faker import Faker
from src.mapping_store import MappingStore
from src.models import Entity

fake = Faker("en_US")

REPLACEMENT_GENERATORS = {
    "PERSON":        lambda: fake.name(),
    "EMAIL":         lambda: fake.email(),
    "PHONE_NUMBER":  lambda: fake.phone_number(),
    "ORGANIZATION":  lambda: fake.company(),
    "ADDRESS":       lambda: fake.address(),
    "US_SSN":        lambda: fake.ssn(),
    "CREDIT_CARD":   lambda: fake.credit_card_number(),
    "DATE_OF_BIRTH": lambda: fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%d/%m/%Y"),
    "IP_ADDRESS":    lambda: fake.ipv4_private(),
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
        for ent, original, replacement in replacements:
            if original in span.text:
                span.text = span.text.replace(original, replacement)
                span.run_ref.text = span.text
