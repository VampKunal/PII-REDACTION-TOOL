import argparse
import docx
from src.extractor import extract_spans
from src.structural_context import propagate_structural_context, tag_table_cells_by_header
from src.preprocessor import preprocess
from src.detector import detect_all
from src.postprocessor import postprocess
from src.validator import validate_entities
from src.replacer import replace_entities, apply_replacements_to_spans
from src.mapping_store import MappingStore
import json

def process_document(input_path: str, output_path: str, mapping_path: str = None):
    print(f"Loading document: {input_path}")
    try:
        doc = docx.Document(input_path)
    except Exception as e:
        print(f"Failed to load document: {e}")
        return

    print("1. Extracting spans...")
    spans = extract_spans(doc)
    
    print("2. Propagating structural context...")
    spans = propagate_structural_context(spans)
    tag_table_cells_by_header(doc, spans)
    
    print("3. Preprocessing text...")
    text, mapping = preprocess(spans)
    
    print("4. Detection...")
    entities = detect_all(text)
    
    print("5. Post-processing...")
    entities = postprocess(entities, text)
    
    print("6. Validation...")
    entities = validate_entities(entities, text)
    
    print("7. Replacement...")
    store = MappingStore(save_path=mapping_path)
    replacements = replace_entities(entities, text, store)
    apply_replacements_to_spans(spans, replacements)
    
    if mapping_path:
        print(f"Saving mappings to {mapping_path}...")
        store.save()
    
    print("8. Saving output...")
    doc.save(output_path)
    print(f"Redacted document saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PII Redaction Tool")
    parser.add_argument("--input", required=True, help="Input DOCX path")
    parser.add_argument("--output", required=True, help="Output DOCX path")
    parser.add_argument("--mapping", required=False, help="Path to save replacement mappings (JSON)", default="output/mapping.json")
    args = parser.parse_args()
    
    process_document(args.input, args.output, args.mapping)
