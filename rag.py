# rag.py
"""
Core RAG (Retrieval-Augmented Generation) pipeline for The Padel Company Chatbot.
Loads embeddings via Hugging Face Serverless API and generates responses via Groq.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("rag_pipeline")

# Lazy loaded caches
_collection = None
_groq_client = None

def get_embedding(text: str) -> List[List[float]]:
    """
    Generates a 384-dimensional vector embedding for a given string.
    Queries the Hugging Face Serverless Inference API.
    
    Args:
        text (str): The input text to be embedded.
        
    Returns:
        List[List[float]]: A 2D list of shape (1, 384) representing the text embedding.
    """
    from huggingface_hub import InferenceClient

    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError(
            "HF_TOKEN environment variable not found. Please configure HF_TOKEN in your environment or .env file.\n"
            "Generate a free token at https://huggingface.co/settings/tokens"
        )
        
    logger.info("Requesting embedding from Hugging Face Inference API...")
    client = InferenceClient(model="sentence-transformers/all-MiniLM-L6-v2", token=hf_token)
    
    try:
        result = client.feature_extraction(text)
    except Exception as e:
        logger.error(f"Hugging Face feature extraction failed: {e}")
        raise ValueError(
            f"Hugging Face Inference API failed: {e}\n\n"
            "TIP: This is usually because of a missing or misconfigured HF_TOKEN.\n"
            "Please ensure:\n"
            "1. You have set HF_TOKEN in your environment variables or Render dashboard.\n"
            "2. Your token has 'Inference' permissions enabled, or use a Legacy 'Read' token."
        ) from e
    
    # Convert numpy array to list if returned as one
    if hasattr(result, "tolist"):
        result = result.tolist()
        
    # Ensure it's returned as a list of lists of floats (2D list) for ChromaDB
    if isinstance(result, list) and len(result) > 0:
        if not isinstance(result[0], list):
            result = [result]
            
    return result

def get_collection() -> Any:
    """
    Lazily initializes and connects to the ChromaDB vector database.
    
    Returns:
        chromadb.Collection: Connected collection instance.
    """
    global _collection
    if _collection is None:
        logger.info("Connecting to ChromaDB persistent collection...")
        import chromadb
        script_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(script_dir, "chroma_db")
        chroma_client = chromadb.PersistentClient(path=db_path)
        _collection = chroma_client.get_collection("padel_docs")
        logger.info("Connected to ChromaDB successfully.")
    return _collection

def get_groq_client() -> Any:
    """
    Lazily initializes the Groq client.
    
    Returns:
        groq.Groq: Groq API client instance.
    """
    global _groq_client
    if _groq_client is None:
        logger.info("Initializing Groq API client...")
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable not found. Please configure it in your environment or .env file."
            )
        _groq_client = Groq(api_key=api_key)
        logger.info("Groq API client initialized successfully.")
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

def retrieve(query: str, top_k: int = 4) -> List[str]:
    """
    Retrieves the top-k most semantically similar text chunks from the vector database.
    
    Args:
        query (str): The search query from the user.
        top_k (int): Number of document chunks to retrieve. Default is 4.
        
    Returns:
        List[str]: A list of relevant context documents.
    """
    logger.info(f"Retrieving context for query: {query}")

    # Convert question into embedding using Hugging Face API
    query_embedding = get_embedding(query)

    # Search ChromaDB
    results = get_collection().query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    documents = results["documents"][0]
    logger.info(f"Retrieved {len(documents)} context chunks successfully.")
    return documents

def generate(query: str, context_chunks: List[str]) -> str:
    """
    Generates a structured answer using the LLM (Llama 3.3 via Groq) based on context chunks.
    
    Args:
        query (str): User's search question.
        context_chunks (List[str]): Context pieces retrieved from vector search.
        
    Returns:
        str: Generated factual response.
    """
    # Combine chunks into one context
    context = "\n\n---\n\n".join(context_chunks)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{query}\n"
        }
    ]

    logger.info("Generating response from Groq API...")
    response = get_groq_client().chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
        max_tokens=512
    )

    answer = response.choices[0].message.content
    logger.info("Response generated successfully from Groq.")
    return answer

def ask(query: str) -> Dict[str, Any]:
    """
    Executes the complete RAG flow: retrieval, context prompts, and LLM text generation.
    
    Args:
        query (str): The user's input question.
        
    Returns:
        Dict[str, Any]: A dictionary containing:
            - "answer" (str): Factual answer from the model.
            - "sources" (List[str]): The context documents used.
    """
    chunks = retrieve(query)
    answer = generate(query, chunks)
    return {
        "answer": answer,
        "sources": chunks
    }