# DocSorter -- OCR & Document Intelligence Demo

DocSorter is a modular OCR-based document processing pipeline designed to simulate a production-style document ingestion backend.


This project simulates a lightweight startup-ready backend system
capable of:

-   Extracting text from PDFs (single and multi-page)
-   Classifying document types (invoice, receipt, contract, ID, etc.)
-   Generating unique document codes
-   Storing structured results in a CSV index
-   Caching OCR results for performance optimization

------------------------------------------------------------------------

## 🚀 What This Project Demonstrates

This repository shows how to build a simplified but production-style:

-   OCR ingestion pipeline
-   Lightweight document classifier
-   Hash-based caching mechanism
-   CSV-based indexing system
-   CLI-driven automation workflow

It is designed as a **portfolio-ready demo project** for:

-   AI / ML roles
-   Backend development roles
-   Document processing automation startups
-   Invoice/finance automation SaaS ideas

------------------------------------------------------------------------

## 🧠 Architecture Overview

    your-repo/
    │
    ├── cli.py                # Command line interface
    │
    ├── src/
    │   ├── cache.py          # Hash-based caching system
    │   ├── ocr.py            # OCR extraction logic
    │   ├── classifier.py     # Rule-based document classification
    │   ├── index.py          # CSV indexing logic
    │   └── __init__.py
    │
    ├── data/
    │   ├── cache.json        # Stores OCR results (hash → pages)
    │   └── index.csv         # Structured document index
    │
    ├── samples/              # Demo PDFs
    ├── out/                  # Generated outputs
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 🧩 Key Engineering Concepts

- Deterministic hashing (SHA-256) for idempotent processing
- Cache-first architecture to avoid redundant OCR computation
- Stateless CLI workflow
- Structured CSV indexing for downstream analytics
- Confidence-based classification scoring

## 📄 How It Works

### 1️⃣ OCR Extraction

-   Extracts text from PDFs
-   Supports multi-page documents
-   Stores page-wise extracted content

### 2️⃣ Hash-Based Caching

-   Each file is hashed using SHA-256
-   If the same file is scanned again, OCR is skipped
-   Results are loaded from `cache.json`

### 3️⃣ Classification

A lightweight rule-based classifier identifies document type:

-   `invoice`
-   `receipt`
-   `contract`
-   `id_document`

Confidence score is calculated based on keyword matches.

### 4️⃣ Indexing

Every processed document is appended to:

    data/index.csv

Structure:

  Column          Description
  --------------- ---------------------------
  timestamp_utc   Processing time
  file_path       Original file path
  file_hash       SHA-256 hash
  doc_type        Predicted type
  doc_code        Generated document code
  confidence      Classification confidence
  pages_count     Number of pages detected

------------------------------------------------------------------------

## 🔄 Typical Workflow

1. Place PDF documents inside `samples/`
2. Run batch processing command
3. OCR extracts text and stores page-level results
4. Classifier assigns document type + confidence
5. Index entry is appended to `data/index.csv`
6. Subsequent runs reuse cached results automatically

## 🛠 Installation

Make sure Python 3.9+ is installed.

Install dependencies:

    pip install -r requirements.txt

If using PowerShell on Windows:

    python -m pip install -r requirements.txt

------------------------------------------------------------------------

## 🧪 Most Useful Commands

### 🔹 Batch Scan All Documents

    python cli.py batch --input samples --out-dir out --index data/index.csv --cache data/cache.json

Processes all PDFs inside `samples/`.

------------------------------------------------------------------------

### 🔹 Scan Single Document

    python cli.py scan --input samples/multipage_invoice_5p.pdf --out out/result.json

Extracts OCR data and saves structured output.

------------------------------------------------------------------------

### 🔹 Test Multi-Page Handling

After running batch, check:

-   `pages_count` in `data/index.csv`
-   Page list inside `data/cache.json`

------------------------------------------------------------------------

## 📦 Example Output

Example entry in `index.csv`:

    2026-02-12T13:54:01.144159+00:00,samples\multipage_invoice_5p.pdf,...,invoice,INV-xxxxxxx,1.0000,5

This confirms:

-   Classified as `invoice`
-   Confidence = 1.0
-   5 pages detected

------------------------------------------------------------------------

## 🔥 Why This Is Interesting

This demo represents a simplified foundation for:

-   Invoice automation SaaS
-   Document workflow systems
-   AI document copilots
-   Finance processing automation
-   Smart document indexing systems

It can be extended with:

-   Real ML models (Logistic Regression / Transformers)
-   Database integration (PostgreSQL)
-   REST API layer (FastAPI)
-   Cloud deployment
-   UI dashboard

------------------------------------------------------------------------

## 🧭 Future Improvements

-   Replace rule-based classifier with trained ML model
-   Add invoice field extraction (total amount, supplier, etc.)
-   Add REST API interface
-   Add vector search over documents
-   Integrate with cloud storage
-   Add monitoring & logging

------------------------------------------------------------------------

## 👨‍💻 Author

Built as a portfolio-grade OCR & document intelligence demo by Bakir Bećić.

------------------------------------------------------------------------

