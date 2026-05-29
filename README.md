#  RAG Chatbot

> An AI-powered customer support chatbot for [thepadelcompany.in](https://thepadelcompany.in) — built with a full Retrieval-Augmented Generation (RAG) pipeline using 100% free-tier tools.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Local_Vector_DB-orange?style=flat-square)
![Groq](https://img.shields.io/badge/Groq-llama3--70b-F55036?style=flat-square)
![HuggingFace](https://img.shields.io/badge/HuggingFace-all--MiniLM--L6--v2-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

##  What this does

Instead of a generic chatbot, this system **reads the actual website**, understands it semantically, and answers user questions strictly from that content minimising hallucinations.

A user asks: *"Which padel coaches are available in Pune?"*  
The bot retrieves the most relevant paragraphs from the site, injects them as context into an LLM, and returns a grounded, accurate answer.

---
##  Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  INGESTION (one-time)                    │
│                                                          │
│  Playwright  →  Chunking  →  Embeddings  →  ChromaDB    │
│  (scrape)       (400 chars)   (384-dim)     (persist)   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               QUERY FLOW (per message)                   │
│                                                          │
│  User question  →  Embed query  →  Top-K retrieval      │
│        ↓                              ↓                  │
│  FastAPI POST /chat          ChromaDB similarity search  │
│        ↓                              ↓                  │
│  Groq LLM  ←──────── context chunks ─────────────────── │
│        ↓                                                 │
│  Grounded answer                                         │
└─────────────────────────────────────────────────────────┘
```

---

##  Tech Stack (100% Free)

| Layer | Tool | Why |
|---|---|---|
| **Scraping** | [Playwright](https://playwright.dev/python/) | Handles JS-rendered pages that `requests` can't see |
| **Chunking** | [LangChain](https://python.langchain.com/) | `RecursiveCharacterTextSplitter` with overlap |
| **Embeddings** | [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) | 384-dim, runs on CPU, no API key |
| **Vector DB** | [ChromaDB](https://www.trychroma.com/) | Local persistence, zero cloud dependency |
| **LLM** | [Groq](https://console.groq.com) | Free tier: ~14,400 req/day, ultra-fast inference |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn | Async, auto-docs at `/docs` |

---

##  Quickstart

### 1. Clone and install

```bash
git clone https://github.com/yourusername/padel-chatbot.git
cd padel-chatbot
pip install -r requirements.txt
playwright install chromium
```

### 2. Set your Groq API key

Get a free key at [console.groq.com](https://console.groq.com)

```bash
export GROQ_API_KEY=your_key_here
```

### 3. Run the pipeline

```bash
# Scrape the website → docs/
python scraper.py

# Embed + store → chroma_db/
python ingest.py

# Start the API server
uvicorn main:app --reload --port 8000
```

### 4. Test it

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What are your court booking prices?"}'
```

---

##  Project Structure

```
padel-chatbot/
├── docs/               ← scraped markdown (auto-created)
├── chroma_db/          ← vector store (auto-created)
├── scraper.py          ← Playwright site scraper
├── ingest.py           ← chunking + embedding pipeline
├── rag.py              ← retrieval + generation logic
├── main.py             ← FastAPI app
├── config.py           ← tunable constants
└── requirements.txt
```

---

##  API Reference

### `POST /chat`

```json
// Request
{ "question": "How much is Elite membership?" }

// Response
{ "answer": "Elite membership includes unlimited court access..." }
```

### `GET /health`

```json
{ "status": "ok" }
```

Auto-generated interactive docs available at `http://localhost:8000/docs`

---

##  Key Concepts

**Why RAG over fine-tuning?**  
Fine-tuning a model on site content is expensive, slow to update, and overkill for a chatbot that needs to reflect live website data. RAG retrieves fresh context at query time, re-run ingest whenever the site updates.

**Why cosine similarity?**  
Embedding vectors encode *direction*, not magnitude. Cosine similarity measures the angle between vectors — two semantically similar sentences produce vectors that point in the same direction regardless of length.

**Why chunk overlap?**  
A sentence can split right across a chunk boundary. Overlap ensures context isn't lost at edges — if the answer spans two adjacent chunks, the overlapping region gives the retriever a chance to capture it.

---

##  Roadmap

- [ ] Streaming responses via SSE
- [ ] Conversation memory (multi-turn)
- [ ] Source citations in answers
- [ ] Auto re-ingestion via GitHub Actions cron
- [ ] Deploy to Render / Railway

---
This project is for educational purposes only.
Data was collected from publicly accessible pages.
