# rag/summarizer.py
import os, time, requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def _fallback_summary(query: str, contexts: list[str]) -> str:
    # simple extractive fallback: take first ~4-6 sentences from contexts
    joined = " ".join(contexts)
    parts = [p.strip() for p in joined.replace("\n", " ").split(". ") if p.strip()]
    excerpt = ". ".join(parts[:5]) + ("." if parts[:5] else "")
    return f"(Fallback summary)\nQuery: {query}\n\n{excerpt or 'Not enough context to summarize.'}"

def summarize_context(query: str, contexts: list[str]) -> str:
    if not OPENAI_API_KEY:
        return _fallback_summary(query, contexts)

    prompt = (
        "You are a concise technical assistant. Using ONLY the context below, "
        "answer the user's query in 4-6 sentences. If info is missing, say so.\n\n"
        f"Query:\n{query}\n\n"
        "Context:\n" + "\n\n---\n\n".join(contexts)
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}

    # retry with exponential backoff on 429/5xx
    for attempt in range(4):  # 0,1,2,3
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** attempt)  # 1s, 2s, 4s, 8s
                continue
            # other errors → break to fallback
            break
        except requests.RequestException:
            time.sleep(2 ** attempt)
            continue

    # fallback if API keeps failing
    return _fallback_summary(query, contexts)
