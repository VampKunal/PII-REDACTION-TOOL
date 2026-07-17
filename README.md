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
- **Consistent Mapping:** If "John Smith" is detected, he will be replaced consistently with a fixed placeholder like `<PERSON>` throughout the entire 500-page document, replacing Faker to prevent real-sounding names from being used as substitutes.
- **Fuzzy & Exact Dictionary Matching:** Ships with JSON lists of top companies and global locations, cross-referenced efficiently via O(N) trie algorithms.
- **Address & Company Suffix Detectors:** Uses highly targeted custom regex matchers for Address Keywords (Road, Street, Sector, etc.) and Company suffixes (Ltd, Pvt Ltd, Inc, etc.) for robust hybrid recognition.
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
python -m spacy download en_core_web_sm
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
   - **Regex Recognizers:** Targets Address Keywords (Road, Street, District, PIN, PO Box) and Company suffixes (Ltd, Inc, Corporation, Trust).
5. **Post-Processing:** Resolves overlapping entities, merges duplicates, drops low-confidence matches, and enforces explicit **Whitelists** (e.g., SEBI, NSE, RBI) and **Heading Blacklists** (e.g., "TABLE OF CONTENTS").
6. **Validation:** Checks entity checksums (e.g., verifying phone numbers via `phonenumbers` and credit cards via `Luhn`).
7. **Replacement:** Replaces validated entities in the document using fixed placeholders (like `<PERSON>`, `<ORGANIZATION>`) inspired by `presidio-anonymizer`, dropping Faker for better data-integrity.

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
3. **`replacer.py`** — add the fixed string substitution logic
4. **`detector.py`** — add context boost/suppress keywords

No changes are needed to the extractor, orchestrator, or output writer!

---

## Evaluation & Metrics

To test the accuracy of the PII redactor (Precision, Recall, and F1-Score), an evaluation script is included: `evaluate.py`.

You will need a JSON file of "Ground Truth" entities (what *should* have been redacted) and compare it against the `mapping.json` outputted by the tool.

```bash
python evaluate.py --truth "data/ground_truth.json" --preds "output/mapping.json"
```

The script will calculate:
- **Precision:** How many of the redacted items were actually PII? (Low False Positives).
- **Recall:** How much of the actual PII in the document did we successfully catch? (Low False Negatives).
- **F1-Score:** The harmonic mean of Precision and Recall.

It also outputs a debug list of exact strings that were missed (False Negatives) or incorrectly redacted (False Positives) so you can easily refine the whitelist and regex rules.

---

## Web Server Configuration (Next.js + FastAPI)

We have transformed this CLI tool into a full-stack web application. The architecture is cleanly divided into a frontend and a backend to ensure scalability and ease of deployment.

### What `pii-redactor` Does
The core `pii-redactor` logic remains the brain of the operation. It is purely responsible for taking a DOCX file in memory, parsing it, passing it through the NLP pipeline (SpaCy, Presidio, Custom Regex), and returning a fully redacted DOCX file along with a JSON mapping. It has no concept of HTTP requests or web clients.

### What the Web Server Does
The web server wraps the `pii-redactor` core to make it accessible over the internet:
1. **Frontend (Next.js):** Provides a beautiful, drag-and-drop user interface for clients to upload documents. It handles the `multipart/form-data` upload and automatically downloads the processed file once returned by the backend. It is hosted on **Vercel**.
2. **Backend (FastAPI):** A high-performance Python asynchronous server. It exposes a `POST /api/redact` endpoint. It receives the uploaded file, saves it to a secure temporary directory, executes the `pii-redactor` pipeline on it, returns the processed file as a downloadable blob, and cleans up the server's local storage immediately after. It is hosted on **Render**.

### Deployment Implementation for GitHub
The deployment is entirely Git-driven (CI/CD):
- **Version Control:** All code is pushed to a single GitHub repository.
- **Frontend CI/CD (Vercel):** Connected directly to the GitHub repo. Any push to `main` triggers Vercel to automatically build the Next.js app and deploy it globally.
- **Backend CI/CD (Render):** Connected directly to the GitHub repo. Any push to `main` triggers Render to automatically pull the Python code, install the heavy ML dependencies from `requirements.txt` (including downloading the SpaCy NLP models), and start the FastAPI web server. The Next.js frontend communicates with the FastAPI backend using environment variables (`NEXT_PUBLIC_API_URL`).
