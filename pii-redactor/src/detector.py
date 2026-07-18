from src.recognizers.presidio_recognizer import detect_presidio
from src.recognizers.spacy_org_recognizer import detect_orgs
from src.recognizers.dict_recognizer import DictionaryRecognizer
from src.recognizers.fuzzy_recognizer import FuzzyRecognizer
from src.recognizers.regex_recognizer import RegexRecognizer

# Initialize recognizers for Orgs and Locations only
# Note: We intentionally DO NOT use dictionary/fuzzy matching for names to avoid false positives.
org_dict_recognizer = DictionaryRecognizer("data/companies.json", "ORGANIZATION")
loc_dict_recognizer = DictionaryRecognizer("data/locations.json", "LOCATION") # cities, states, countries
org_fuzzy_recognizer = FuzzyRecognizer("data/companies.json", "ORGANIZATION", threshold=85.0)

ADDR_REGEX = r"(?i)\b(?:\d+\s+)?(?:[A-Z][a-z0-9]+\s+){0,3}(?:Road|Street|Sector|Village|Taluka|District|Tower|Apartment|Building|Floor|Branch|Park)\b(?:\s+\d+[a-zA-Z]*)?|\b(?:PO Box|P\.O\.\s*Box)\s+\d+\b|\b(?:PIN|Pincode|Pin\s*Code)\s*\d{6}\b"
COMP_REGEX = r"\b(?:[A-Z][a-zA-Z0-9&]*\s+){1,4}(?:Ltd|Limited|Pvt\s*Ltd|LLP|Inc|Corporation|Trust|Foundation|Infra|Logistics|Motors|Electricals)\b"
PHONE_REGEX = r"(?i)\b(?:Tel|Phone|Mob|Mobile|Ph)\s*[:\.]?\s*(?:\+?\d[\d\-\s]{7,15})\b"
PAN_REGEX = r"(?i)\b[A-Z]{5}\d{4}[A-Z]\b"
USERNAME_REGEX = r"(?i)\b[a-z]+_[a-z0-9_]+\b" # Captures things like mchang_official, admin_root

addr_regex_recognizer = RegexRecognizer(ADDR_REGEX, "ADDRESS", score=0.6)
comp_regex_recognizer = RegexRecognizer(COMP_REGEX, "ORGANIZATION", score=0.6)
phone_regex_recognizer = RegexRecognizer(PHONE_REGEX, "PHONE_NUMBER", score=0.8)
pan_regex_recognizer = RegexRecognizer(PAN_REGEX, "PAN_NUMBER", score=1.0)
username_regex_recognizer = RegexRecognizer(USERNAME_REGEX, "USERNAME", score=0.9)

def detect_all(text: str) -> list:
    entities = []
    chunk_size = 10000
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
        
        addr_regex_ents = addr_regex_recognizer.detect(chunk)
        comp_regex_ents = comp_regex_recognizer.detect(chunk)
        phone_regex_ents = phone_regex_recognizer.detect(chunk)
        pan_regex_ents = pan_regex_recognizer.detect(chunk)
        username_regex_ents = username_regex_recognizer.detect(chunk)
        
        # Adjust offsets
        all_ents = presidio_ents + spacy_ents + dict_org_ents + dict_loc_ents + fuzzy_org_ents + addr_regex_ents + comp_regex_ents + phone_regex_ents + pan_regex_ents + username_regex_ents
        for ent in all_ents:
            ent.start += start
            ent.end += start
            entities.append(ent)
            
    print("      - Done detection!")
    
    return entities
