from pathlib import Path

import fitz
import PIL.Image


def extract_pages(path: Path) -> list[dict]:
    doc = fitz.open(str(path))
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages


def is_text_pdf(path: Path) -> bool:
    doc = fitz.open(str(path))
    if not doc.page_count:
        doc.close()
        return False
    total_chars = sum(len(page.get_text("text")) for page in doc)
    avg = total_chars / doc.page_count
    doc.close()
    return avg >= 50


def render_page_to_image(path: Path, page_no: int, dpi: int = 200) -> PIL.Image.Image:
    doc = fitz.open(str(path))
    page = doc[page_no - 1]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img = PIL.Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    return img
