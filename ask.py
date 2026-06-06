import os
import argparse
from dotenv import load_dotenv
from groq import Groq
from embed import retrieve

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask(question):
    chunks = retrieve(question, k=5)
    
    context = ""
    sources = []
    for chunk in chunks:
        context += f"[Source: {chunk['source']}]\n{chunk['text']}\n\n"
        if chunk['source'] not in sources:
            sources.append(chunk['source'])

    prompt = f"""You are a helpful assistant answering questions about Purdue CS professors based only on student reviews and forum posts.

Answer the question using ONLY the information in the provided documents below.
If the documents don't contain enough information to answer the question, say exactly:
"I don't have enough information in my documents to answer that."

Do not use any outside knowledge. Cite which source(s) your answer draws from.

Documents:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )

    answer = response.choices[0].message.content.strip()
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ask a question about Purdue CS professors")
    parser.add_argument("question", type=str, help="Your question")
    args = parser.parse_args()

    result = ask(args.question)
    print("\nAnswer:")
    print(result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(f"  • {s}")
