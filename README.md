# CampusIQ — Professional College RAG Assistant
### Prathyusha Engineering College (Autonomous)

CampusIQ is an AI-powered college knowledge assistant designed specifically for **Prathyusha Engineering College (PEC)**. It enables students, faculty, and visitors to ask college-related questions in natural language and receive strictly grounded, verified answers from official college knowledge sources.

---

## 🏛️ System Architecture

```
                                  CAMPUSIQ
                                      │
                     React Frontend (Editorial University UI)
                     [Warm Ivory #F7F1E8 | Deep Burgundy #5A1020]
                                      │
                               FastAPI Backend
                                      │
                 ┌────────────────────┴────────────────────┐
                 │                                         │
        Conversation Service                        RAG Engine
        (SQLite Chat History)                              │
        - Today / Yesterday / Earlier                      │
        - Search, Rename, Delete                           │
                                                           │
                                      ┌────────────────────┴────────────────────┐
                                      │                                         │
                               College Documents                         Social Media
                          (PDF/DOCX/TXT via PyMuPDF)             (PEC LinkedIn, Instagram, YouTube)
                                      │                                         │
                                      └────────────────────┬────────────────────┘
                                                           │
                                              Structural & Semantic Chunking
                                                           │
                                                  Qwen3-Embedding-8B
                                                  (4096 Dimensions)
                                                           │
                                                Qdrant Vector Database
                                                           │
                                                  Top-K Retrieval
                                           + Temporal & Provenance Boost
                                                           │
                                           Answerability & Grounding Check
                                                           │
                                                     Gemini LLM
                                                           │
                                             Grounded Response + Sources
```

---

## ⚙️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **React 19 + Vite** | Responsive UI with "Premium Editorial University" aesthetic |
| **Backend** | **Python + FastAPI** | High-performance asynchronous REST API |
| **Vector DB** | **Qdrant** | 4096-dimensional Cosine vector search with metadata filtering |
| **Embeddings** | **Qwen3-Embedding-8B** | 4096-dimensional embeddings with configurable provider pattern |
| **LLM** | **Gemini** | Factually grounded answer generation with strict zero-hallucination rules |
| **Ingestion** | **PyMuPDF (`fitz`), python-docx** | High-fidelity PDF, DOCX, and TXT document parsing |
| **Social Media** | **LinkedIn, Instagram, YouTube** | Multi-source knowledge indexing with actual post/video URLs |
| **Chat History** | **SQLite** | Persistent relational storage decoupled from vector database |
| **Voice** | **Local Whisper & Web Speech** | Speech-to-text recording with preview & modular TTS architecture |

---

## 🌐 Configured Official PEC Knowledge Channels

CampusIQ indexes knowledge exclusively from verified official sources:

1. **Official PEC LinkedIn**: [`https://www.linkedin.com/school/prathyushaenggcollege/`](https://www.linkedin.com/school/prathyushaenggcollege/)
2. **Official PEC Instagram**: [`https://www.instagram.com/prathyushainstitute/`](https://www.instagram.com/prathyushainstitute/)
3. **Official PEC YouTube**: [`https://youtube.com/@prathyushaengineeringcollege`](https://youtube.com/@prathyushaengineeringcollege)
4. **Official PEC Website**: [`https://prathyusha.edu.in`](https://prathyusha.edu.in)
5. **Official College Documents**: Academic Calendar, Bus Boarding Timings, Hostel Facilities & Rules, Mess Menu (July 2026), Student Dress Code, and Clubs/Innovation Domains (`data/college_documents/`).

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.9+ installed
- Node.js 18+ and npm installed
- Google Gemini API key configured in `.env` (`GOOGLE_API_KEY=...`)

### 2. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Build & Index the Knowledge Base
To index all college documents and official social media into Qdrant:
```bash
python build_vectorstore.py
```
*Output: 4096-dimensional vectors created in `vectorstore/qdrant/`.*

### 4. Start the Application

You can run the application in two ways:

#### Option A: Unified Full-Stack (FastAPI serves compiled React frontend)
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

#### Option B: Separate Frontend Development Server
```bash
# Terminal 1: Backend
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: React Frontend
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🔒 Grounding & Anti-Hallucination Principles

CampusIQ strictly adheres to:
1. **Source of Truth**: The assistant answers ONLY from verified context retrieved from Qdrant.
2. **Safe Fallback**: If information is absent or partial:
   > *"I couldn't find verified information about this in the available Prathyusha Engineering College sources. Please contact the concerned college office directly for the current procedure."*
3. **Zero Fabrication**: CampusIQ NEVER invents phone numbers, office rooms, staff names, fees, deadlines, or URLs.
4. **Source Provenance**: Every grounded answer contains transparent citations with genuine document titles or live verified links to PEC YouTube videos, LinkedIn posts, and Instagram updates.
