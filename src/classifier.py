from __future__ import annotations

import json
from pathlib import Path
from typing import List, Tuple, Optional, Any, Dict


LABELS = ["invoice", "receipt", "contract", "id_document", "unknown"]


def _join_pages_text(pages: List[Dict[str, Any]]) -> str:
    return "\n".join((p.get("text") or "") for p in pages).strip()


def _heuristic_predict(text: str) -> Tuple[str, float]:
    t = text.lower()

   
    invoice_hits = sum(k in t for k in ["invoice", "vat", "subtotal", "total due", "bill to", "invoice no", "tax"])
    
    receipt_hits = sum(k in t for k in ["receipt", "cashier", "change", "store", "pos", "paid", "thank you"])
    
    contract_hits = sum(k in t for k in ["agreement", "contract", "terms", "party", "hereby", "governed by", "signature"])
    
    id_hits = sum(k in t for k in ["identity", "passport", "nationality", "date of birth", "id number", "place of birth"])

    scores = {
        "invoice": invoice_hits,
        "receipt": receipt_hits,
        "contract": contract_hits,
        "id_document": id_hits,
    }

    best = max(scores, key=scores.get)
    best_score = scores[best]
    if best_score == 0:
        return ("unknown", 0.20)


    total = sum(scores.values()) or 1
    conf = 0.50 + 0.50 * (best_score / total)  # 0.5-1.0
    return (best, float(conf))


def load_model(model_path: str):
    p = Path(model_path)
    if not p.exists():
        return None
    try:
        import joblib  
        return joblib.load(p)
    except Exception:
        return None


def predict_document(pages: List[Dict[str, Any]], model=None) -> Tuple[str, float]:
    text = _join_pages_text(pages)
    if not text:
        return ("unknown", 0.10)


    if model is not None:
        try:
            proba = model.predict_proba([text])[0]
            pred_idx = int(proba.argmax())
            label = model.classes_[pred_idx]
            conf = float(proba[pred_idx])

            if label not in LABELS:
                return _heuristic_predict(text)
            return (label, conf)
        except Exception:
            return _heuristic_predict(text)

    return _heuristic_predict(text)


def train_model(train_path: str, model_path: str) -> None:
    p = Path(train_path)
    if not p.exists():
        raise RuntimeError(
            f"Training dataset ne postoji: {train_path}\n"
            "Ocekujem JSONL, npr:\n"
            '{"text":"Invoice No 123 ...", "label":"invoice"}'
        )

    texts: List[str] = []
    labels: List[str] = []

    with p.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                text = (obj.get("text") or "").strip()
                label = (obj.get("label") or "").strip()
                if not text or not label:
                    continue
                texts.append(text)
                labels.append(label)
            except Exception as e:
                raise RuntimeError(f"Nevalidan JSONL na liniji {line_no}: {e}")

    if len(texts) < 5:
        raise RuntimeError("Premalo trening primjera. Dodaj bar ~20 linija za demo ML.")

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  
        from sklearn.linear_model import LogisticRegression  
        from sklearn.pipeline import Pipeline 
        import joblib  
    except Exception as e:
        raise RuntimeError(
            "Za trening treba scikit-learn + joblib.\n"
            f"Detalji: {e}"
        )

    clf = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("lr", LogisticRegression(max_iter=2000)),
        ]
    )

    clf.fit(texts, labels)

    out = Path(model_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, out)
