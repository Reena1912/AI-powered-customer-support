# 🎾 The Padel Company — AI Support Chatbot

An AI-powered customer support chatbot for [thepadelcompany.in](https://thepadelcompany.in) built with a full Retrieval-Augmented Generation (RAG) pipeline using **FastAPI**, **ChromaDB**, **SentenceTransformers**, and **Groq's LPU** (Llama 3.3).

Backend Live URL: https://ai-powered-customer-support-7xkn.onrender.com

Frontend Live URL: https://ai-powered-customer-support-eight.vercel.app

---

## 🎨 System Architecture

The project splits into an offline ingestion phase and a real-time query phase:

```mermaid
graph TD
    subgraph Offline Ingestion
        A[scraper.py] -->|1. Web Scraping| B[docs/*.md]
        B -->|2. load_and_chunk| C[ingest.py]
        C -->|3. SentenceTransformer all-MiniLM-L6-v2| D[Embeddings]
        D -->|4. Store & Persist| E[(ChromaDB: padel_docs)]
    end

    subgraph Real-Time Query Flow
        F[Frontend UI /chat] -->|1. Question| G[FastAPI main.py]
        G -->|2. Encode Query| H[rag.py retrieve]
        H -->|3. Similarity Query| E
        E -->|4. Top-K Chunks| H
        H -->|5. Context + Prompt| I[Groq Llama 3.3-70B]
        I -->|6. Generative Answer| G
        G -->|7. JSON Response| F
    end

    style E fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style I fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style G fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
```

---

## ✨ Key Features

* **Lazy-Loading Architecture**: Starts in `<200ms` globally. Embedding model and database connections are loaded dynamically on the first query. Highly optimized for memory-constrained cloud environments (such as Render's 512MB free tier) to prevent Out-Of-Memory (OOM) crashes.
* **Minimalist Brand Match UI**: Responsive HTML/CSS/JS frontend featuring clickable suggested questions, emojis, scrolling state persistence, and styling aligned with the light theme of `thepadelcompany.in`.
* **Zero-Hallucination Guardrails**: Prompts are constrained to answer strictly from the retrieved database context, falling back politely to a contact message if the context does not contain the answer.
* **Local Embedding Processing**: Generates embeddings locally using `all-MiniLM-L6-v2` (384-dimensional vectors) on CPU without external API dependency.

---

## 🏗️ Project Directory Structure

```text
AI-powered-customer-support/
├── docs/               # Scraped pages + custom context (pricing, listings, bookings, partnerships)
├── chroma_db/          # Persistent local vector store (auto-created during ingestion)
├── frontend/           # Chat Web Interface
│   ├── index.html      # Responsive chat viewport with clickable suggestions
│   ├── style.css       # Minimalist light-mode stylesheet matching the official brand look
│   └── app.js          # API connection, bubble renderer, and typing indicators
├── main.py             # FastAPI backend server
├── rag.py              # Core RAG search and completions pipeline (lazy-loaded)
├── ingest.py           # Chunking and embedding generation pipeline
├── scraper.py          # Playwright-based website scraper script
├── requirements.txt    # Python dependencies
└── .gitignore          # Git exclusion rules for secrets, DBs, and venvs
```

---

## 🚀 Local Installation & Setup

### Prerequisites
* Python 3.9, 3.10, 3.11, or 3.12 (Python 3.10+ recommended)
* A Groq API Key (Free tier at [console.groq.com](https://console.groq.com))

### Step-by-Step Installation
1. **Clone or navigate** to the project directory:
   ```bash
   cd AI-powered-customer-support
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # On Windows (PowerShell/CMD)
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright Browsers** (only needed if running the scraper):
   ```bash
   playwright install chromium
   ```

5. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

---

## 💻 How to Run Locally

### 1. Build/Rebuild the Vector Index
Parse the markdown documents in `docs/` and ingest them into the vector database:
```bash
python ingest.py
```
*Note: This creates the `chroma_db/` folder locally.*

### 2. Start the Backend API
Run the Uvicorn ASGI server:
```bash
uvicorn main:app --port 8000
```
* The API will be active at `http://127.0.0.1:8000`
* You can test and inspect the endpoints interactively at `http://127.0.0.1:8000/docs`

### 3. Run the Chat UI
Serve the frontend files locally using Python's static file server in a separate terminal:
```bash
python -m http.server 3000 --directory frontend
```
Open your browser and navigate to **`http://localhost:3000`**.

---

## 📡 API Specification

### `POST /chat`
Sends a user query to the RAG pipeline.

* **Request URL**: `http://localhost:8000/chat`
* **Content-Type**: `application/json`
* **Payload**:
  ```json
  {
    "question": "What are your court booking prices?"
  }
  ```
* **Response (Success - 200 OK)**:
  ```json
  {
    "answer": "Court booking prices are set by individual venue operators and typically range from ₹800 to ₹2,500 per hour across India, depending on the city, facility quality, and time of play."
  }
  ```

### `GET /health`
A simple check to ensure the backend is running.

* **Request URL**: `http://localhost:8000/health`
* **Response (Success - 200 OK)**:
  ```json
  {
    "status": "ok"
  }
  ```

---

## ⚙️ Parameter Tuning & Configuration

You can customize the chunking strategies and retrieval thresholds:

### Ingest Parameters (`ingest.py`)
Modify the `RecursiveCharacterTextSplitter` args to adjust chunk granularity:
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,     # Size of each text chunk (in characters)
    chunk_overlap=50,   # Overlap between adjacent chunks to maintain context
    separators=["\n\n", "\n", " "]
)
```

### RAG Parameters (`rag.py`)
* **Retrieve Count (`top_k`)**: Inside `retrieve(query, top_k=4)`, adjust `top_k` to pass more or fewer context snippets to the LLM.
* **Inference Settings**: Adjust the completions parameters inside `generate()`:
  ```python
  response = get_groq_client().chat.completions.create(
      model="llama-3.3-70b-versatile",
      temperature=0.1,    # Low temperature (0.1) reduces hallucinations
      max_tokens=512      # Adjust output answer length
  )
  ```

---

