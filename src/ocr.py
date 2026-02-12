from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class OCRPage:
    page: int
    text: str

    def to_dict(self) -> Dict[str, Any]:
        return {"page": self.page, "text": self.text}


def _try_extract_pdf_text(pdf_path: str) -> List[OCRPage]:
    try:
        from pypdf import PdfReader
    except Exception:
        return []

    try:
        reader = PdfReader(pdf_path)
        pages: List[OCRPage] = []
        for i, p in enumerate(reader.pages):
            t = p.extract_text() or ""
            pages.append(OCRPage(page=i + 1, text=t.strip()))
        # ako je sve prazno, tretiraj kao "nema teksta"
        if all(len(pg.text) == 0 for pg in pages):
            return []
        return pages
    except Exception:
        return []


def _tesseract_ocr_image_pil(pil_img, lang: str) -> str:
    import pytesseract  # type: ignore

    # minimal config (mozes kasnije dotjerati)
    return pytesseract.image_to_string(pil_img, lang=lang).strip()


def _ocr_pdf_with_tesseract(pdf_path: str, lang: str) -> List[OCRPage]:
    # Convert PDF pages to images then OCR
    try:
        from pdf2image import convert_from_path  # type: ignore
        images = convert_from_path(pdf_path, dpi=200)
    except Exception as e:
        raise RuntimeError(
            "Ne mogu OCR-ati PDF. Treba: pdf2image + poppler, i pytesseract.\n"
            f"Detalji: {e}"
        )

    pages: List[OCRPage] = []
    for i, img in enumerate(images):
        text = _tesseract_ocr_image_pil(img, lang=lang)
        pages.append(OCRPage(page=i + 1, text=text))
    return pages


def _ocr_image_file(path: str, lang: str) -> List[OCRPage]:
    try:
        from PIL import Image  # type: ignore
        img = Image.open(path)
    except Exception as e:
        raise RuntimeError(f"Ne mogu otvoriti sliku: {path} -> {e}")

    try:
        text = _tesseract_ocr_image_pil(img, lang=lang)
    except Exception as e:
        raise RuntimeError(
            "Ne mogu uraditi OCR na slici. Treba: pytesseract + Tesseract instaliran.\n"
            f"Detalji: {e}"
        )

    return [OCRPage(page=1, text=text)]


def ocr_file(path: str, lang: str = "eng") -> List[Dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    ext = p.suffix.lower()

    if ext == ".pdf":
        # 1) probaj normal extraction (brzo i bez OCR)
        extracted = _try_extract_pdf_text(str(p))
        if extracted:
            return [pg.to_dict() for pg in extracted]

        # 2) fallback OCR
        ocred = _ocr_pdf_with_tesseract(str(p), lang=lang)
        return [pg.to_dict() for pg in ocred]

    if ext in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}:
        pages = _ocr_image_file(str(p), lang=lang)
        return [pg.to_dict() for pg in pages]

    raise RuntimeError(f"Nepodrzan format: {ext}")
