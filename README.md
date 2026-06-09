# 🤖 Gemini RAG Chatbot (Streamlit + ChromaDB)

A ChatGPT-style AI chatbot that lets you upload a PDF and ask questions about it using:

- Google Gemini API
- ChromaDB (Vector Database)
- Sentence Transformers (Embeddings)
- Streamlit (UI)
- PyPDF (PDF reader)

---

## Demo

![Demo](screenshot/demo 4.png)

---

# 🚀 Features

- 📄 Upload any PDF file
- 🧠 AI understands document content using RAG
- 🔍 Semantic search with embeddings
- 💬 ChatGPT-style UI
- 🗂 Context-aware answers using ChromaDB
- 🧾 Conversation memory

---

# 🏗 Project Workflow

PDF Upload
↓
Text Extraction (PyPDF)
↓
Chunking
↓
Embeddings (SentenceTransformer)
↓
Store in ChromaDB
↓
User Question
↓
Similarity Search
↓
Gemini Response
