# rag/retriever.py
import chromadb
from fastembed import TextEmbedding

COLLECTION_NAME = "clean_docs_index"

def retrieve(query: str, k: int = 3):
    # same persistence path and collection used by indexer
    client = chromadb.PersistentClient(path="./chroma")
    coll = client.get_or_create_collection(name=COLLECTION_NAME)

    # embed the query with the same model as indexer
    embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    qvec = list(embedder.embed([query]))[0]  # 1 vector

    res = coll.query(
        query_embeddings=[qvec],
        n_results=k,
        include=["metadatas", "documents", "distances"],  # no "ids" here
    )

    out = []
    ids = res.get("ids", [[]])[0]  # ids are returned by default
    for i in range(len(ids)):
        out.append({
            "id": ids[i],
            "distance": res["distances"][0][i],
            "url": res["metadatas"][0][i].get("url"),
            "title": res["metadatas"][0][i].get("title"),
            "snippet": (res["documents"][0][i][:220] + "…"),
        })
    return out

if __name__ == "__main__":
    hits = retrieve("python programming news and releases", k=3)
    for h in hits:
        print(f"* {h['title']}  ({h['url']})  dist={h['distance']:.4f}")
