# rag/indexer.py
import chromadb
from fastembed import TextEmbedding
from db_clean import get_clean_collection

COLLECTION_NAME = "clean_docs_index"

def build_index(limit: int = 200):
    # Init Chroma (no embedding_function — we pass embeddings ourselves)
    client = chromadb.PersistentClient(path="./chroma")
    coll = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Load cleaned docs from Mongo
    mongo = get_clean_collection()
    docs = list(mongo.find({}, {"_id": 1, "url": 1, "domain": 1, "title": 1, "full_text": 1}).limit(limit))
    if not docs:
        print("No cleaned docs found. Run processing/benchmark.py or save_clean_doc first.")
        return

    ids   = [str(d["_id"]) for d in docs]
    texts = [d.get("full_text", "") for d in docs]
    metas = [{"url": d.get("url",""), "domain": d.get("domain",""), "title": d.get("title","")} for d in docs]

    # Compute embeddings with FastEmbed (no Torch)
    embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    embeddings = list(embedder.embed(texts))  # generator -> list of vectors

    coll.upsert(ids=ids, documents=texts, metadatas=metas, embeddings=embeddings)
    print(f"Indexed {len(ids)} documents into collection '{COLLECTION_NAME}' at ./chroma")

if __name__ == "__main__":
    build_index()
