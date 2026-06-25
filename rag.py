from dotenv import load_dotenv
import os

load_dotenv()

# -----------------------------
# Lazy Loading Helpers
# -----------------------------
_model = None
_collection = None
_groq_client = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Embedding model loaded!")
    return _model

def get_collection():
    global _collection
    if _collection is None:
        print("Connecting to ChromaDB...")
        import chromadb
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "chroma_db")
        chroma_client = chromadb.PersistentClient(path=db_path)
        _collection = chroma_client.get_collection("padel_docs")
        print("Connected to ChromaDB!")
    return _collection

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set the GROQ_API_KEY environment variable."
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client

# -----------------------------
# System Prompt
# -----------------------------
SYSTEM_PROMPT = """
You are a helpful assistant for The Padel Company website.

1. If the user's message is a greeting (like 'hi', 'hello', 'hey', etc.) or asks who you are, respond politely and explain that you can help them find courts, coaches, tournaments, bookings, and racket marketplace listings in India.

2. The user may send short, keyword-based queries (e.g., "more franchise", "court bookings", "price"). Interpret these as requests for information on those topics and answer them using the provided context.

3. Answer all questions strictly using the provided context. Only say:
"I don't have that information — please contact us directly."
if the context has no relevant information on the topic at all.

4. Never make up information.
"""

# -----------------------------
# Retrieve relevant chunks
# -----------------------------
def retrieve(query: str, top_k: int = 4):

    print(f"Retrieving chunks for: {query}")

    # Convert question into embedding
    query_embedding = get_model().encode([query]).tolist()

    # Search ChromaDB
    results = get_collection().query(
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

    response = get_groq_client().chat.completions.create(
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