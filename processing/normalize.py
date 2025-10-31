# processing/normalize.py
from urllib.parse import urlparse
from dataclasses import dataclass, asdict
from typing import Optional
from bs4 import BeautifulSoup

from processing.cleaner import clean_html_to_text

@dataclass
class CleanRecord:
    url: str
    domain: str
    title: Optional[str]
    length: int
    preview: str
    full_text: str

def extract_title(html: str) -> Optional[str]:
    soup = BeautifulSoup(html or "", "html.parser")
    t = soup.find("title")
    return t.get_text(strip=True) if t else None

def normalize_raw_item(raw: dict, preview_len: int = 240) -> dict:
    """
    raw should contain keys: url, html
    returns a JSON-serializable dict ready for DB.
    """
    url = raw.get("url", "")
    domain = urlparse(url).netloc
    title = extract_title(raw.get("html", ""))
    text = clean_html_to_text(raw.get("html", ""))
    rec = CleanRecord(
        url=url,
        domain=domain,
        title=title,
        length=len(text),
        preview=text[:preview_len],
        full_text=text,
    )
    return asdict(rec)
