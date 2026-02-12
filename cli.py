import argparse
import json
from pathlib import Path

from src.cache import compute_file_hash, load_cache, save_cache
from src.ocr import ocr_file
from src.classifier import load_model, predict_document, train_model
from src.index import ensure_index_exists, append_index_row, make_doc_code


def cmd_scan(args):
    cache = load_cache(args.cache)

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input ne postoji: {input_path}")

    h = compute_file_hash(str(input_path))

    if h in cache:
        payload = cache[h]
        print("cache_hit")
    else:
        pages = ocr_file(str(input_path), lang=args.lang)
        payload = {
            "input": str(input_path),
            "hash": h,
            "pages": pages,
        }
        cache[h] = payload
        save_cache(cache, args.cache)
        print("processed")

    # Snimi OCR JSON output ako je trazeno
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Klasifikacija
    model = load_model(args.model) if args.model else None
    doc_type, confidence = predict_document(payload["pages"], model=model)

    # Upis u index.csv ako je trazeno
    if args.index:
        ensure_index_exists(args.index)
        code = make_doc_code(doc_type, payload["hash"])
        append_index_row(
            index_path=args.index,
            file_path=str(input_path),
            file_hash=payload["hash"],
            doc_type=doc_type,
            doc_code=code,
            confidence=confidence,
            pages_count=len(payload["pages"]),
        )
        print(f"indexed -> {args.index}")

    print(f"type={doc_type} confidence={confidence:.2f}")


def cmd_batch(args):
    in_dir = Path(args.input)
    if not in_dir.exists() or not in_dir.is_dir():
        raise SystemExit(f"Input folder ne postoji: {in_dir}")

    ensure_index_exists(args.index)
    cache = load_cache(args.cache)
    model = load_model(args.model) if args.model else None

    exts = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}

    files = [p for p in in_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]
    if not files:
        print("Nema fajlova za obradu.")
        return

    out_dir = Path(args.out_dir) if args.out_dir else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    processed_count = 0
    for f in files:
        h = compute_file_hash(str(f))

        if h in cache:
            payload = cache[h]
        else:
            pages = ocr_file(str(f), lang=args.lang)
            payload = {"input": str(f), "hash": h, "pages": pages}
            cache[h] = payload

        doc_type, confidence = predict_document(payload["pages"], model=model)
        code = make_doc_code(doc_type, payload["hash"])

        append_index_row(
            index_path=args.index,
            file_path=str(f),
            file_hash=payload["hash"],
            doc_type=doc_type,
            doc_code=code,
            confidence=confidence,
            pages_count=len(payload["pages"]),
        )

        if out_dir:
            # snimi ocr json per file
            out_json = out_dir / f"{f.stem}.{payload['hash'][:8]}.json"
            out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        processed_count += 1

    save_cache(cache, args.cache)
    print(f"batch_done files={processed_count} index={args.index} cache={args.cache}")


def cmd_train(args):
    # Ocekuje data/train_samples.jsonl (ili putanju koju das)
    # JSONL format: {"text": "...", "label": "invoice"} po liniji
    model_path = args.model
    train_path = args.train

    train_model(train_path=train_path, model_path=model_path)
    print(f"trained -> {model_path}")


def main():
    parser = argparse.ArgumentParser(prog="your-repo", description="OCR + Document Classification Demo CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_scan = sub.add_parser("scan", help="OCR + classify one file (pdf/image)")
    p_scan.add_argument("--input", required=True, help="Putanja do PDF-a ili slike")
    p_scan.add_argument("--out", default=None, help="Gdje snimiti OCR JSON (npr out/result.json)")
    p_scan.add_argument("--lang", default="eng", help="OCR jezik (tesseract), default eng")
    p_scan.add_argument("--cache", default="data/cache.json", help="Cache json putanja")
    p_scan.add_argument("--index", default="data/index.csv", help="CSV index putanja")
    p_scan.add_argument("--model", default="data/model.joblib", help="Model putanja (ako ne postoji, fallback heuristika)")
    p_scan.set_defaults(func=cmd_scan)

    p_batch = sub.add_parser("batch", help="OCR + classify all files in folder (recursive)")
    p_batch.add_argument("--input", required=True, help="Folder sa pdf/slikama")
    p_batch.add_argument("--out-dir", default="out", help="Folder za OCR JSON outputs")
    p_batch.add_argument("--lang", default="eng", help="OCR jezik (tesseract), default eng")
    p_batch.add_argument("--cache", default="data/cache.json", help="Cache json putanja")
    p_batch.add_argument("--index", default="data/index.csv", help="CSV index putanja")
    p_batch.add_argument("--model", default="data/model.joblib", help="Model putanja (ako ne postoji, fallback heuristika)")
    p_batch.set_defaults(func=cmd_batch)

    p_train = sub.add_parser("train", help="Train ML model from JSONL dataset")
    p_train.add_argument("--train", default="data/train_samples.jsonl", help="JSONL dataset putanja")
    p_train.add_argument("--model", default="data/model.joblib", help="Gdje snimiti model")
    p_train.set_defaults(func=cmd_train)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
