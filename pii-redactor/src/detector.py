from src.recognizers.presidio_recognizer import detect_presidio
from src.recognizers.spacy_org_recognizer import detect_orgs
from src.recognizers.dict_recognizer import DictionaryRecognizer
from src.recognizers.fuzzy_recognizer import FuzzyRecognizer

# Initialize recognizers for Orgs and Locations only
# Note: We intentionally DO NOT use dictionary/fuzzy matching for names to avoid false positives.
org_dict_recognizer = DictionaryRecognizer("data/companies.json", "ORGANIZATION")
loc_dict_recognizer = DictionaryRecognizer("data/locations.json", "LOCATION") # cities, states, countries
org_fuzzy_recognizer = FuzzyRecognizer("data/companies.json", "ORGANIZATION", threshold=85.0)

def detect_all(text: str) -> list:
    entities = []
    chunk_size = 50000
    overlap = 100
    
    total_chunks = (len(text) // chunk_size) + 1
    
    for i in range(total_chunks):
        start = i * chunk_size
        # To avoid splitting words/entities, we could add overlap, but for simplicity let's just chunk
        # with a small overlap and deduplicate later (postprocessor handles dedup).
        end = min((i + 1) * chunk_size + overlap, len(text))
        
        chunk = text[start:end]
        if not chunk.strip():
            continue
            
        print(f"      - Processing chunk {i+1}/{total_chunks} ({len(chunk)} chars)...")
        
        presidio_ents = detect_presidio(chunk)
        spacy_ents = detect_orgs(chunk)
        dict_org_ents = org_dict_recognizer.detect(chunk)
        dict_loc_ents = loc_dict_recognizer.detect(chunk)
        fuzzy_org_ents = org_fuzzy_recognizer.detect(chunk)
        
        # Adjust offsets
        for ent in presidio_ents + spacy_ents + dict_org_ents + dict_loc_ents + fuzzy_org_ents:
            ent.start += start
            ent.end += start
            entities.append(ent)
            
    print("      - Done detection!")
    
    return entities
