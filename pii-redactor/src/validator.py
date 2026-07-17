import phonenumbers
import re

def validate_phone(candidate: str) -> bool:
    try:
        parsed = phonenumbers.parse(candidate, "IN") # Default to IN, but parses +XX correctly
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        return False

def luhn_check(card_number: str) -> bool:
    digits = [int(x) for x in str(card_number) if x.isdigit()]
    if not digits:
        return False
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    return checksum % 10 == 0

def validate_credit_card(candidate: str) -> bool:
    digits = re.sub(r"\D", "", candidate)
    return luhn_check(digits) and 13 <= len(digits) <= 19

def validate_entity(entity, text_candidate: str) -> bool:
    if entity.label == "PHONE_NUMBER":
        return validate_phone(text_candidate)
    if entity.label == "CREDIT_CARD":
        return validate_credit_card(text_candidate)
    # Return true for those that don't need strict validation right now
    return True

def validate_entities(entities: list, text: str) -> list:
    validated = []
    for ent in entities:
        if validate_entity(ent, text[ent.start:ent.end]):
            validated.append(ent)
    return validated
