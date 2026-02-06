import argparse
import json
from pathlib import Path

from src.cache import compute_file_hash, load_cache, save_cache
from src.ocr import ocr_file

def cmd_scan(args):
    cache = load_cache()
    h = compute_file_hash(args.input)

    if h in cache:
        print("cache_hit")
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(
            json.dumps(cache[h], ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return

    pages = ocr_file(args.input, lang=args.lang)

    payload = {
        "input": args.input,
        "hash": h,
        "pages": pages
    }

    cache[h] = payload
    save_cache(cache)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print("processed")

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan")
    scan.add_argument("--input", required=True)
    scan.add_argument("--out", default="outputs/ocr.json")
    scan.add_argument("--lang", default="eng")
    scan.set_defaults(func=cmd_scan)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
