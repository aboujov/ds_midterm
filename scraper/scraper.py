import requests
from bs4 import BeautifulSoup

def scrape_titles(url: str, limit: int = 10):
    """
    Fetch page and extract article titles.
    - For Hacker News: uses 'span.titleline a'
    - Fallback: all <h2> tags (common on blogs/news sites)
    """
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    titles = []

    # 1) Hacker News structure
    for a in soup.select("span.titleline a"):
        titles.append(a.get_text(strip=True))
        if len(titles) >= limit:
            break

    # 2) Fallback to <h2> if nothing found
    if not titles:
        for h2 in soup.find_all("h2"):
            titles.append(h2.get_text(strip=True))
            if len(titles) >= limit:
                break

    return {"url": url, "count": len(titles), "titles": titles}

if __name__ == "__main__":
    print(scrape_titles("https://news.ycombinator.com"))
