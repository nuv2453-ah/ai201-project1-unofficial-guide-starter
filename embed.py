import json
import chromadb
from sentence_transformers import SentenceTransformer

def embed_and_store(chunks_path="chunks.json", collection_name="purdue_cs"):
    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"Embedding {len(chunks)} chunks...")

    texts = [chunk["text"] for chunk in chunks]
    sources = [chunk["source"] for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    embeddings = model.encode(texts, show_progress_bar=True)

    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(collection_name)
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=[{"source": s} for s in sources],
        ids=ids
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{collection_name}'")
    return collection

def retrieve(query, collection_name="purdue_cs", k=5):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode([query]).tolist()

    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(collection_name)

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i]
        })
    return chunks

if __name__ == "__main__":
    embed_and_store()

    test_queries = [
        "Does Borkowski curve exams in CS 251?",
        "Are Sellke's lectures easy to follow?",
        "How hard is CS 180 with Bergstrom?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        results = retrieve(query)
        for r in results:
            print(f"Source: {r['source']} | Distance: {r['distance']:.3f}")
            print(f"Text: {r['text'][:150]}")
            print()
