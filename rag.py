from dotenv import load_dotenv
load_dotenv()

from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
import os

# -----------------------------
# Check API key
# -----------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. "
        "Create a .env file and add:\n"
        "GROQ_API_KEY=your_api_key"
    )

print("Groq API key loaded successfully!")

# -----------------------------
# Load embedding model
# -----------------------------
print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded!")

# -----------------------------
# Connect to ChromaDB
# -----------------------------
print("Connecting to ChromaDB...")

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_collection("padel_docs")

print("Connected to ChromaDB!")

# -----------------------------
# Initialize Groq client
# -----------------------------
groq_client = Groq(api_key=GROQ_API_KEY)

# -----------------------------
# System Prompt
# -----------------------------
SYSTEM_PROMPT = """
You are a helpful assistant for The Padel Company website.

Answer ONLY using the context provided below.

If the context does not contain the answer,
say:
"I don't have that information — please contact us directly."

Never make up information.
"""

# -----------------------------
# Retrieve relevant chunks
# -----------------------------
def retrieve(query: str, top_k: int = 4):

    print(f"Retrieving chunks for: {query}")

    # Convert question into embedding
    query_embedding = model.encode([query]).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    documents = results["documents"][0]

    print(f"Retrieved {len(documents)} chunks")

    return documents

# -----------------------------
# Generate final answer
# -----------------------------
def generate(query: str, context_chunks):

    # Combine chunks into one context
    context = "\n\n---\n\n".join(context_chunks)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""
Context:
{context}

Question:
{query}
"""
        }
    ]

    print("Generating response from Groq...")

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=512
    )

    answer = response.choices[0].message.content

    return answer

# -----------------------------
# Main RAG pipeline
# -----------------------------
def ask(query: str):

    chunks = retrieve(query)

    answer = generate(query, chunks)

    return {
        "answer": answer,
        "sources": chunks
    }