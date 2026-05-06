from pathlib import Path
import PIL.Image


def extract_pages(path: Path) -> list[dict]:
    raise NotImplementedError


def is_text_pdf(path: Path) -> bool:
    raise NotImplementedError


def render_page_to_image(path: Path, page_no: int, dpi: int = 200) -> PIL.Image.Image:
    raise NotImplementedError
