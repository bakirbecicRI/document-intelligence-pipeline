from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path


HEADER = [
    "timestamp_utc",
    "file_path",
    "file_hash",
    "doc_type",
    "doc_code",
    "confidence",
    "pages_count",
]


def ensure_index_exists(index_path: str) -> None:
    p = Path(index_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if not p.exists():
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(HEADER)


def make_doc_code(doc_type: str, file_hash: str) -> str:
    # npr INV-1a2b3c4d
    prefix = {
        "invoice": "INV",
        "receipt": "RCP",
        "contract": "CTR",
        "id_document": "IDD",
        "unknown": "UNK",
    }.get(doc_type, "UNK")
    return f"{prefix}-{file_hash[:8]}"


def append_index_row(
    index_path: str,
    file_path: str,
    file_hash: str,
    doc_type: str,
    doc_code: str,
    confidence: float,
    pages_count: int,
) -> None:
    p = Path(index_path)
    if not p.exists():
        ensure_index_exists(index_path)

    ts = datetime.now(timezone.utc).isoformat()

    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                ts,
                file_path,
                file_hash,
                doc_type,
                doc_code,
                f"{confidence:.4f}",
                str(pages_count),
            ]
        )
