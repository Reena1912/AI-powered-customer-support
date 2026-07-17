# ingest.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Check if local model can be loaded, otherwise fallback to serverless Hugging Face API
use_local_model = False
try:
    from sentence_transformers import SentenceTransformer
    use_local_model = True
except ModuleNotFoundError:
    print("sentence-transformers not found. Falling back to Hugging Face Serverless Inference API for embeddings.")

def load_and_chunk(docs_dir="docs") -> list:
    """Loads all Markdown documents in docs_dir and splits them into semantic chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " "]
    )

    chunks = []
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        print(f"Documents directory {docs_dir} does not exist.")
        return chunks

    for file in docs_path.glob("*.md"):
        print(f"Reading {file.name}")
        text = file.read_text(encoding="utf-8")
        pieces = splitter.split_text(text)

        for piece in pieces:
            chunks.append({
                "text": piece,
                "source": file.name
            })

    print(f"\nCreated {len(chunks)} chunks from source documents.")
    return chunks

def get_embeddings(texts: list) -> list:
    """Generates embedding vectors for a list of texts using local model or HF API."""
    if use_local_model:
        print(f"Generating local embeddings for {len(texts)} chunks using sentence-transformers...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(texts, show_progress_bar=True).tolist()
        return embeddings
    else:
        from huggingface_hub import InferenceClient
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError(
                "HF_TOKEN environment variable is required to generate embeddings via Hugging Face Serverless API. "
                "Please configure HF_TOKEN in your environment or .env file."
            )
        
        print(f"Requesting embeddings for {len(texts)} chunks via Hugging Face Serverless API...")
        client = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2", token=hf_token)
        
        embeddings = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            res = client.feature_extraction(batch)
            if hasattr(res, "tolist"):
                res = res.tolist()
            
            # Ensure return shape is 2D list of floats
            if isinstance(res, list) and len(res) > 0:
                if not isinstance(res[0], list):
                    res = [res]
            embeddings.extend(res)
        return embeddings

def build_vector_store(chunks: list):
    """Builds and populates the persistent vector index."""
    if not chunks:
        print("No chunks provided. Skipping vector store build.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    
    try:
        client.delete_collection("padel_docs")
    except Exception:
        pass
    collection = client.create_collection("padel_docs")

    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]

    embeddings = get_embeddings(texts)

    # Add in batches to ChromaDB to ensure clean execution
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        collection.add(
            documents=texts[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=[{"source": s} for s in sources[i:i+batch_size]],
            ids=[str(j) for j in range(i, min(i+batch_size, len(texts)))]
        )
    print(f"Vector store successfully built and saved to {db_path}!")

if __name__ == "__main__":
    chunks = load_and_chunk()
    build_vector_store(chunks)