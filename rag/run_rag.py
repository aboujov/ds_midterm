# rag/run_rag.py
from rag.retriever import retrieve
from rag.summarizer import summarize_context

def run(query: str, k: int = 3):
    hits = retrieve(query, k=k)
    # take the text snippets as context
    contexts = [h["snippet"] for h in hits]
    answer = summarize_context(query, contexts)
    print("=== QUERY ===")
    print(query)
    print("\n=== ANSWER ===")
    print(answer)
    print("\n=== SOURCES ===")
    for h in hits:
        print(f"- {h['title']} ({h['url']})  dist={h['distance']:.4f}")

if __name__ == "__main__":
    run("python programming news and releases", k=3)
