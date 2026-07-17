import json
from pathlib import Path

class MappingStore:
    def __init__(self, save_path: str = None):
        self.save_path = save_path
        self.store = {
            "PERSON": {},
            "EMAIL": {},
            "PHONE_NUMBER": {},
            "ORGANIZATION": {},
            "ADDRESS": {},
            "US_SSN": {},
            "CREDIT_CARD": {},
            "DATE_OF_BIRTH": {},
            "IP_ADDRESS": {}
        }
        
    def get_replacement(self, entity_type: str, original: str, generator_fn) -> str:
        # Fallback category if not initialized
        if entity_type not in self.store:
            self.store[entity_type] = {}
            
        if original not in self.store[entity_type]:
            self.store[entity_type][original] = generator_fn()
            
        return self.store[entity_type][original]

    def save(self, path: str = None):
        target = path or self.save_path
        if target:
            with open(target, 'w') as f:
                json.dump(self.store, f, indent=2)
