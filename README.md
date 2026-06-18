# 🎾 The Padel Company — AI Support Chatbot

An AI-powered customer support chatbot for [thepadelcompany.in](https://thepadelcompany.in) — built with a Retrieval-Augmented Generation (RAG) pipeline using ChromaDB, sentence-transformers, and Groq's Llama 3.3 model.

---

## ✨ Features

* **Lazy-Loading Architecture**: Boots instantly (in `<200ms`) and defers model loading until the first query. Highly optimized for memory-constrained cloud environments (such as Render's 512MB free tier) to prevent Out-Of-Memory (OOM) crashes.
* **Semantic Search & RAG**: Automatically reads local markdown knowledge documents, chunks and encodes them using `all-MiniLM-L6-v2` embeddings, and queries ChromaDB for similarity matches.
* **Fast Inference**: Connects to the Groq API utilizing `llama-3.3-70b-versatile` for lightning-fast completions.
* **Premium Minimalist UI**: A beautiful, user-friendly, responsive chat interface designed to match the minimalist light-mode branding of the official website.

---

## 🏗️ Project Structure

```text
AI-powered-customer-support/
├── docs/               # Scraped pages + custom context (pricing, listings, bookings)
├── chroma_db/          # Persistent local vector store (auto-created during ingestion)
├── frontend/           # Chat Web Interface
│   ├── index.html      # Responsive chat viewport with clickable suggestions
│   ├── style.css       # Clean minimalist stylesheet matching the official brand look
│   └── app.js          # API connection, bubble renderer, and typing indicators
├── main.py             # FastAPI backend server
├── rag.py              # Core RAG search and completions pipeline (lazy-loaded)
├── ingest.py           # Chunking and embedding generation pipeline
└── requirements.txt    # Python dependencies
```

---

## 🚀 Local Setup & Execution

### 1. Install Dependencies
Make sure you have Python installed, navigate to the project directory, activate your virtual environment, and install dependencies:
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project folder and paste your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Build the Vector Index
Run the ingestion script to process your markdown files and build the vector database:
```bash
python ingest.py
```

### 4. Run the Backend API
Start your FastAPI server using Uvicorn:
```bash
uvicorn main:app --port 8000
```
Your backend will be running at `http://localhost:8000` with interactive API docs available at `http://localhost:8000/docs`.

### 5. Run the Chat UI
Serve the frontend static files on port `3000`:
```bash
python -m http.server 3000 --directory frontend
```
Now, open your web browser and navigate to **`http://localhost:3000`** to chat with the assistant!

---

## ☁️ Cloud Deployment (Render & Vercel)

### 1. Deploy the Backend to Render
Render provides free hosting for Python applications. 
1. Push your code to a GitHub repository (your `.gitignore` is already set up to exclude local caches and credentials).
2. Create a new **Web Service** on Render and connect your repository.
3. Configure the settings:
   * **Runtime**: `Python`
   * **Build Command**: `pip install -r requirements.txt && python ingest.py` *(This automatically generates your database index at build time so you don't need persistent cloud storage).*
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variable**:
   * Key: `GROQ_API_KEY`
   * Value: `your_actual_groq_api_key`
5. Click **Deploy**. Render will provide a public URL (e.g., `https://your-backend.onrender.com`).

### 2. Deploy the Frontend to Vercel/Netlify
1. Open `frontend/app.js` and update the `API_URL` to point to your live Render backend instead of localhost:
   ```javascript
   const API_URL = 'https://your-backend.onrender.com/chat';
   ```
2. Commit and push the changes to GitHub.
3. Connect your repository to **Vercel** or **Netlify**.
4. Set the **Root Directory** to `frontend` and click **Deploy**.
