from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

def load_and_chunk(docs_dir="docs"):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " "]
    )

    chunks = []

    for file in Path(docs_dir).glob("*.md"):

        print(f"Reading {file.name}")

        text = file.read_text(encoding="utf-8")

        pieces = splitter.split_text(text)

        for piece in pieces:
            chunks.append({
                "text": piece,
                "source": file.name
            })

    print(f"\nCreated {len(chunks)} chunks")

    return chunks

def build_vector_store(chunks):
    # Free model — runs on CPU, no API key needed
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Persistent local DB — data survives restarts
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete and recreate if re-ingesting
    try:
        client.delete_collection("padel_docs")
    except:
        pass
    collection = client.create_collection("padel_docs")

    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]

    print("Generating embeddings (takes ~30s on CPU)...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    # Add in batches to avoid memory issues
    batch_size = 100
    for i in range(0, len(texts), batch_size):
        collection.add(
            documents=texts[i:i+batch_size],
            embeddings=embeddings[i:i+batch_size],
            metadatas=[{"source": s} for s in sources[i:i+batch_size]],
            ids=[str(j) for j in range(i, min(i+batch_size, len(texts)))]
        )
    print("Vector store built!")



if __name__ == "__main__":
    chunks = load_and_chunk()
    build_vector_store(chunks)