"""Text extraction for documents and source-code files; OCR is optional."""
from __future__ import annotations

import io
import os
from pathlib import Path

from docx import Document
import fitz
from PIL import Image

_OCR_READER = None
_OCR_ATTEMPTED = False


def _ocr_image_bytes(data: bytes) -> str:
    global _OCR_READER, _OCR_ATTEMPTED
    if not _OCR_ATTEMPTED:
        _OCR_ATTEMPTED = True
        try:
            import easyocr
            _OCR_READER = easyocr.Reader(["en"], gpu=False)
        except Exception as exc:
            print(f"Optional OCR unavailable: {exc}")
            _OCR_READER = None
    if _OCR_READER is None:
        return ""
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
        import numpy as np
        results = _OCR_READER.readtext(np.array(image), detail=0, paragraph=True)
        return "\n".join(str(item).strip() for item in results if str(item).strip())
    except Exception as exc:
        print(f"OCR failed: {exc}")
        return ""


def extract_text_from_document(file_path: str) -> str:
    path = Path(file_path)
    if not path.is_file():
        return ""
    ext = path.suffix.lower().lstrip(".")
    text = ""

    if ext == "pdf":
        try:
            with fitz.open(path) as pdf:
                pages = []
                for page in pdf:
                    page_text = page.get_text("text") or ""
                    if not page_text.strip():
                        # OCR rendered page only if optional EasyOCR is available.
                        try:
                            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                            page_text = _ocr_image_bytes(pix.tobytes("png"))
                        except Exception:
                            page_text = ""
                    pages.append(page_text)
                text = "\n".join(pages)
        except Exception as exc:
            raise ValueError(f"Could not read PDF: {exc}") from exc

    elif ext in ("docx",):
        try:
            doc = Document(path)
            chunks = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    chunks.extend(cell.text for cell in row.cells if cell.text.strip())
            text = "\n".join(chunks)
        except Exception as exc:
            raise ValueError(f"Could not read DOCX: {exc}") from exc

    elif ext == "doc":
        try:
            import mammoth
            with path.open("rb") as stream:
                text = mammoth.extract_raw_text(stream).value
        except Exception as exc:
            raise ValueError(f"Could not read DOC file: {exc}") from exc

    else:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="cp1252", errors="replace")
        except Exception as exc:
            raise ValueError(f"Could not read text file: {exc}") from exc

    return text.strip()
