# processing/cleaner.py
import re
from bs4 import BeautifulSoup

WHITESPACE_RE = re.compile(r"\s+")

def clean_html_to_text(raw_html: str) -> str:
    """
    Removes <script>, <style>, and all HTML tags.
    Collapses whitespace and returns plain UTF-8 text.
    """
    soup = BeautifulSoup(raw_html or "", "html.parser")

    # remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # get visible text
    text = soup.get_text(separator=" ")

    # normalize whitespace
    text = WHITESPACE_RE.sub(" ", text).strip()

    return text
