import os
import json

def load_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            documents.append({"text": text, "source": filename})
    return documents

def clean_text(text):
    import re
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def chunk_text(doc, chunk_size=300, overlap=50):
    text = clean_text(doc["text"])
    source = doc["source"]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if len(chunk) > 0:
            chunks.append({"text": chunk, "source": source})
        start += chunk_size - overlap
    return chunks

if __name__ == "__main__":
    docs = load_documents("documents")
    print(f"Loaded {len(docs)} documents")

    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc)
        all_chunks.extend(chunks)

    print(f"Total chunks: {len(all_chunks)}")

    print("\n--- 5 SAMPLE CHUNKS ---")
    import random
    for chunk in random.sample(all_chunks, min(5, len(all_chunks))):
        print(f"\nSource: {chunk['source']}")
        print(f"Text: {chunk['text']}")
        print("-" * 40)

    with open("chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2)
    print("\nChunks saved to chunks.json")
