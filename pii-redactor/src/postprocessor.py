from src.models import Entity

WHITELIST = {
    "SEBI", "NSE", "BSE", "RBI", "IRDAI", "AMFI",
    "IPO", "FPO", "OFS",
    "DETAILS OF THE OFFER TO PUBLIC",
    "RISK FACTORS",
    "OBJECTS OF THE OFFER",
}

HEADING_BLACKLIST = {
    "TABLE OF CONTENTS",
    "PROMOTER SELLING SHAREHOLDER",
    "ELIGIBILITY",
    "DETAILS OF OFFER",
    "DISCLAIMER",
    "DEFINITIONS AND ABBREVIATIONS",
    "GENERAL INFORMATION",
    "CONTACT PERSON",
    "TELEPHONE",
    "TEL",
    "PHONE",
    "MOBILE",
    "EMAIL",
    "E-MAIL",
    "FAX",
    "PROMOTERS",
    "PROMOTER",
    "NAME",
}

def resolve_overlaps(entities: list[Entity]) -> list[Entity]:
    entities.sort(key=lambda e: (e.start, -e.score))
    result = []
    last_end = -1
    for ent in entities:
        if ent.start >= last_end:
            result.append(ent)
            last_end = ent.end
        else:
            if ent.score > result[-1].score:
                result[-1] = ent
    return result

def deduplicate(entities: list[Entity]) -> list[Entity]:
    seen = {}
    for ent in entities:
        key = (ent.start, ent.end, ent.label)
        if key in seen:
            seen[key].score = max(seen[key].score, ent.score)
            if ent.source not in seen[key].sources:
                seen[key].sources.append(ent.source)
        else:
            seen[key] = ent
    return list(seen.values())

def apply_threshold(entities: list[Entity], threshold: float) -> list[Entity]:
    return [e for e in entities if e.score >= threshold]

def apply_whitelist(entities: list[Entity], text: str) -> list[Entity]:
    return [
        e for e in entities
        if text[e.start:e.end].strip().upper() not in WHITELIST
    ]

def apply_heading_blacklist(entities: list[Entity], text: str) -> list[Entity]:
    return [
        e for e in entities
        if text[e.start:e.end].strip().upper() not in HEADING_BLACKLIST
    ]

def postprocess(entities: list[Entity], text: str, threshold: float = 0.60) -> list[Entity]:
    ents = deduplicate(entities)
    ents = resolve_overlaps(ents)
    ents = apply_threshold(ents, threshold)
    ents = apply_whitelist(ents, text)
    ents = apply_heading_blacklist(ents, text)
    return ents
