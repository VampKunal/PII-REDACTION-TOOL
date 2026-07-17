from src.models import TextSpan

HEADING_CONTEXT_RULES = {
    "OUR PROMOTER":         "PERSON",
    "PROMOTERS":            "PERSON",
    "PROMOTER":             "PERSON",
    "REGISTERED OFFICE":    "ADDRESS",
    "CORPORATE OFFICE":     "ADDRESS",
    "BRANCH FACILITY":      "ADDRESS",
    "LOCATIONS":            "ADDRESS",
    "BRANCH":               "ADDRESS",
    "DIRECTORS":            "PERSON",
    "BOARD OF DIRECTORS":   "PERSON",
    "KEY MANAGERIAL PERSONNEL": "PERSON",
    "CONTACT DETAILS":      "CONTACT",
    "CONTACT PERSON":       "PERSON",
}

def is_section_boundary(span: TextSpan) -> bool:
    # A simple heuristic: if it's empty, or looks like a major heading (e.g. all caps, short)
    text = span.text.strip()
    if not text:
        return True
    return False

def propagate_structural_context(spans: list[TextSpan]) -> list[TextSpan]:
    current_context = None
    for span in spans:
        upper = span.text.strip().upper()
        # Check if this span IS a heading trigger
        matched = False
        for trigger, label in HEADING_CONTEXT_RULES.items():
            if trigger in upper and len(upper) < len(trigger) + 20: # Ensure it's mostly the heading
                current_context = label
                span.forced_label = None   # heading itself not redacted
                matched = True
                break
        
        if not matched:
            if current_context and span.text.strip():
                span.forced_label = current_context
        
        if is_section_boundary(span):
            current_context = None
            
    return spans

def tag_table_cells_by_header(doc, spans: list[TextSpan]):
    TABLE_TRIGGERS = {
        "REGISTERED OFFICE": "ADDRESS",
        "CORPORATE OFFICE": "ADDRESS",
        "ADDRESS": "ADDRESS",
        "BRANCH FACILITY": "ADDRESS",
        "LOCATIONS": "ADDRESS",
        "BRANCH": "ADDRESS",
        "CONTACT PERSON": "PERSON",
        "PROMOTERS": "PERSON",
        "PROMOTER": "PERSON",
        "NAME": "PERSON",
        "TELEPHONE": "PHONE_NUMBER",
        "TEL": "PHONE_NUMBER",
        "PHONE": "PHONE_NUMBER",
        "MOBILE": "PHONE_NUMBER",
        "EMAIL": "EMAIL",
        "E-MAIL": "EMAIL",
        "FAX": "PHONE_NUMBER"
    }
    
    # To map doc objects to spans, we could index spans by run_ref
    run_to_span = {id(s.run_ref): s for s in spans}
    
    for table in doc.tables:
        for row in table.rows:
            if not row.cells: continue
            
            # Find if the first cell matches any trigger
            first_cell_text = row.cells[0].text.strip().upper()
            
            # Exact or partial match for triggers in the first cell
            forced_label = None
            for trigger, label in TABLE_TRIGGERS.items():
                if trigger in first_cell_text:
                    forced_label = label
                    break
                    
            if forced_label:
                # Force the label on all subsequent cells in the row
                for cell in row.cells[1:]:
                    for para in cell.paragraphs:
                        for run in para.runs:
                            span = run_to_span.get(id(run))
                            if span:
                                span.forced_label = forced_label

def normalize_caps(text: str) -> str:
    words = text.split()
    upper_count = sum(1 for w in words if w.isupper() and len(w) > 4)
    if len(words) > 0 and upper_count / len(words) > 0.8:
        return " ".join(
            w if (w.isupper() and len(w) <= 4) else w.title()
            for w in words
        )
    return text
