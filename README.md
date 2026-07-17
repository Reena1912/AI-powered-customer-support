# The Padel Company — AI Support Chatbot

An AI-powered customer support chatbot for [thepadelcompany.in](https://thepadelcompany.in) that answers queries about courts, coaches, listings, and racket sales in India. 

* **Frontend UI (Vercel)**: https://ai-powered-customer-support-eight.vercel.app
* **Backend API (Render)**: https://ai-powered-customer-support-7xkn.onrender.com

---

## What the Chatbot Does

The chatbot is fed with official website context to help users with:
* **Court Locations & Booking**: Guides players on finding padel courts across India, booking via partnering applications (Playo, Hudle, KheloMore), and general court pricing (ranges from ₹800 to ₹2,500/hr).
* **Coaching Programs**: Recommends professional padel coaches and lists availability in major cities like Pune.
* **Racket Marketplace**: Provides step-by-step guidance on how to buy, list, or sell used padel rackets on the platform's marketplace.
* **Franchise Partnerships**: Answers queries regarding setting up courts, structural support, and court franchise partnerships in India.

---

## Local Setup

### Installation
1. Clone the repository and configure your environment:
   ```bash
   git clone https://github.com/Reena1912/AI-powered-customer-support.git
   cd AI-powered-customer-support
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_key
   HF_TOKEN=your_huggingface_token
   ```

### Running Locally
* **Run Ingestion**: `python ingest.py`
* **Start Backend**: `uvicorn main:app --reload`
* **Start Frontend**: `python -m http.server 3000 --directory frontend`

---

## Testing

Run tests locally:
```bash
pytest
```

Pushing to the `main` branch automatically triggers the test suite on GitHub Actions.
