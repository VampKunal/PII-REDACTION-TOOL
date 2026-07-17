import argparse
import json
from typing import List, Dict, Set

def load_entities(filepath: str) -> List[Dict]:
    """Load entities from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_entity_set(entities: List[Dict]) -> Set[tuple]:
    """Convert a list of entity dictionaries into a set of tuples for easy comparison.
    Assuming entities have 'text' and 'entity_type' keys.
    """
    return set((ent.get("text", "").strip().lower(), ent.get("entity_type", "").upper()) for ent in entities)

def evaluate(ground_truth_path: str, predictions_path: str):
    """
    Evaluates the performance of the PII Redactor using Precision, Recall, and F1-Score.
    """
    try:
        ground_truth = load_entities(ground_truth_path)
        predictions_raw = load_entities(predictions_path)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    # Convert the real mapping.json format (dict of dicts) to our list format if needed
    predictions = []
    if isinstance(predictions_raw, dict):
        for ent_type, mapping in predictions_raw.items():
            for text, _ in mapping.items():
                predictions.append({"text": text, "entity_type": ent_type})
    else:
        predictions = predictions_raw

    gt_set = get_entity_set(ground_truth)
    pred_set = get_entity_set(predictions)

    # Calculate True Positives, False Positives, False Negatives
    true_positives = gt_set.intersection(pred_set)
    false_positives = pred_set - gt_set
    false_negatives = gt_set - pred_set

    tp = len(true_positives)
    fp = len(false_positives)
    fn = len(false_negatives)

    # Calculate Metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    print("=== PII Redaction Evaluation Results ===")
    print(f"Total Ground Truth Entities : {len(gt_set)}")
    print(f"Total Predicted Entities    : {len(pred_set)}")
    print("-" * 40)
    print(f"True Positives (TP)         : {tp}")
    print(f"False Positives (FP)        : {fp}")
    print(f"False Negatives (FN)        : {fn}")
    print("-" * 40)
    print(f"Precision                   : {precision:.4f} ({precision * 100:.2f}%)")
    print(f"Recall                      : {recall:.4f} ({recall * 100:.2f}%)")
    print(f"F1-Score                    : {f1_score:.4f} ({f1_score * 100:.2f}%)")
    print("========================================")

    # Optional: Print out the specific errors for debugging
    if fp > 0:
        print("\n[False Positives - Redacted but shouldn't have been]:")
        for ent in list(false_positives)[:5]:  # Show max 5
            print(f"  - '{ent[0]}' ({ent[1]})")
        if fp > 5: print(f"  ... and {fp - 5} more.")

    if fn > 0:
        print("\n[False Negatives - Missed by redactor]:")
        for ent in list(false_negatives)[:5]:  # Show max 5
            print(f"  - '{ent[0]}' ({ent[1]})")
        if fn > 5: print(f"  ... and {fn - 5} more.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate PII Redaction Performance")
    parser.add_argument("--truth", required=True, help="Path to ground truth JSON file")
    parser.add_argument("--preds", required=True, help="Path to predictions JSON file (e.g., mapping.json)")
    args = parser.parse_args()

    evaluate(args.truth, args.preds)
