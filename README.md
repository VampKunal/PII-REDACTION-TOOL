# PII Redaction Tool

A production-grade Python CLI tool that ingests `.docx` files (especially financial and legal documents like Red Herring Prospectuses) and outputs a fully redacted version where all detected Personally Identifiable Information (PII) is replaced with realistic, internally-consistent fake values.

Designed for **high recall** (miss nothing), **controlled precision** (via explicit whitelist/blacklist), and straightforward **extensibility**.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Architecture & Pipeline](#architecture--pipeline)
- [Why These Architectural Choices?](#why-these-architectural-choices)
- [Extending the Tool](#extending-the-tool)

---

## Features

- **Format-Preserving:** Modifies documents at the lowest `Run` level. All bolding, italics, fonts, and table layouts are preserved flawlessly.
- **Structural Context Awareness:** Uses document headings (e.g., `OUR PROMOTER`, `REGISTERED OFFICE`) to aggressively detect names and addresses in the lines that follow, even if they aren't standard names.
- **Zero API Keys Required:** Runs 100% locally using SpaCy, Presidio, Aho-Corasick, and RapidFuzz. No sensitive documents are ever sent to a third-party server.
- **Consistent Mapping:** If "John Smith" is replaced with "David Martinez", he will be called "David Martinez" throughout the entire 500-page document.
- **Fuzzy & Exact Dictionary Matching:** Ships with JSON lists of top companies and global locations, cross-referenced efficiently via O(N) trie algorithms.
- **Chunked Processing:** Easily processes multi-megabyte Word documents (like Prospectuses) without running out of memory.

---

## Installation

This tool requires Python 3.10+.

1. **Clone and setup a virtual environment:**
```bash
git clone https://github.com/your-org/pii-redaction-tool.git
cd pii-redaction-tool
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

2. **Install core dependencies:**
```bash
pip install -r requirements.txt
```

3. **Download the SpaCy NER Model:**
Because we use SpaCy to detect `ORGANIZATION` entities, you must download the pre-trained Large English Model:
```bash
python -m spacy download en_core_web_lg
```

---

## Usage

You can run the tool directly from the CLI:

```bash
python main.py --input "path/to/contract.docx" --output "output/redacted.docx"
```

To specify where the JSON replacement mapping should be saved (for audit trails):
```bash
python main.py --input "docs/sample.docx" --output "output/redacted.docx" --mapping "output/my_mapping.json"
```

---

## Architecture & Pipeline

The tool runs a 7-stage pipeline optimized for complex legal formats:

1. **Extraction:** Pulls text from Body Paragraphs, Tables, Rows, Cells, Headers, and Footers, creating a `TextSpan` object that maintains a reference to the original DOCX `Run`.
2. **Structural Context Propagation:** Evaluates headings. If it sees `OUR PROMOTER`, it tags following entities as `PERSON`. If a table row starts with `REGISTERED OFFICE`, it tags the following cells as `ADDRESS`. It also title-cases ALL-CAPS paragraphs to improve NER accuracy.
3. **Preprocessing:** Normalizes Unicode, whitespace, and joins wrapped words.
4. **Detection Ensemble:** 
   - **Presidio:** Catches emails, phones, SSNs, standard names.
   - **SpaCy ORG:** Specialized extraction for organizations, with score boosting for keywords like `TRUST`, `LTD`, `PVT`.
   - **Aho-Corasick & RapidFuzz:** Exact and fuzzy dictionary matching exclusively for Organizations and Locations (Cities/States/Countries).
5. **Post-Processing:** Resolves overlapping entities, merges duplicates, drops low-confidence matches, and enforces explicit **Whitelists** (e.g., SEBI, NSE, RBI) and **Heading Blacklists** (e.g., "TABLE OF CONTENTS").
6. **Validation:** Checks entity checksums (e.g., verifying phone numbers via `phonenumbers` and credit cards via `Luhn`).
7. **Replacement:** Replaces validated entities in the document using `Faker` generators, recording the change in a centralized `MappingStore`.

---

## Why These Architectural Choices?

* **No Regex for Company Names:** Company names are entirely free-form. We rely on SpaCy `ORG` combined with Context rules (e.g., boosting a phrase if followed by "Family Trust") rather than brittle regex.
* **No Dictionary Matching for Person Names:** Matching against lists of common names leads to terrible precision. A dictionary match for "Hope" or "Chase" will redact standard verbs. Names are strictly handled by Presidio & SpaCy.
* **Chunked Processing:** Feeding 450,000 characters to NLP models causes exponential parsing slowdowns. The detector chunks text into 50k character blocks, allowing 2MB prospectuses to be processed in seconds.
* **Run-Level Replacement:** Replacing text blindly using string-replace destroys Word document XML structure. We operate directly on `span.run_ref.text`.

---

## Extending the Tool

Extending the tool to a new PII type (e.g., **Driver's License Number**) requires changes in exactly 4 places, keeping the codebase Open-Closed:

1. **`regex_recognizer.py`** — add the pattern (if regex-detectable)
2. **`validator.py`** — add a specific validator function
3. **`replacer.py`** — add the `Faker` generator
4. **`detector.py`** — add context boost/suppress keywords

No changes are needed to the extractor, orchestrator, or output writer!
