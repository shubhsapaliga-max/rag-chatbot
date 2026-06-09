import os
import streamlit as st
import chromadb
import google.generativeai as genai

from dotenv import load_dotenv
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Gemini RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Gemini RAG Chatbot")
st.caption("Chat with your PDF using Gemini + ChromaDB")

# =========================
# LOAD ENVIRONMENT VARIABLES
# =========================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "Upload a PDF",
    type="pdf"
)

# =========================
# LOAD RAG SYSTEM
# =========================

@st.cache_resource(show_spinner=False)
def load_rag(pdf_file):

    gemini_model = genai.GenerativeModel(
        "gemini-3-flash-preview"
    )

    embedding_model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    pdf = PdfReader(pdf_file)

    full_text = ""

    for page in pdf.pages:

        text = page.extract_text()

        if text:
            full_text += text + "\n"

    chunks = []

    chunk_size = 500

    for i in range(0, len(full_text), chunk_size):

        chunk = full_text[i:i + chunk_size]

        if chunk.strip():
            chunks.append(chunk)

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    collection_name = "pdf_collection"

    try:
        client.delete_collection(
            name=collection_name
        )
    except:
        pass

    collection = client.create_collection(
        name=collection_name
    )

    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings
    )

    return (
        gemini_model,
        embedding_model,
        collection
    )

# =========================
# WAIT FOR PDF
# =========================

if uploaded_file is None:

    st.info(
        "📄 Please upload a PDF to start chatting."
    )

    st.stop()

# =========================
# BUILD VECTOR DATABASE
# =========================

with st.spinner(
    "Processing PDF..."
):

    gemini_model, embedding_model, collection = load_rag(
        uploaded_file
    )

st.success("PDF processed successfully!")

# =========================
# SESSION STATE
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT HISTORY
# =========================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

# =========================
# CHAT INPUT
# =========================

question = st.chat_input(
    "Ask a question about the PDF..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    query_embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    retrieved_docs = results["documents"][0]

    context = "\n\n".join(
        retrieved_docs
    )

    history_text = "\n".join(
        [
            f"{m['role']}: {m['content']}"
            for m in st.session_state.messages[-10:]
        ]
    )

    prompt = f"""
You are a helpful AI assistant.

Use ONLY the provided context to answer.

If the answer cannot be found in the context,
reply with:

"I could not find that information in the document."

Conversation History:
{history_text}

Context:
{context}

User Question:
{question}
"""

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            response = gemini_model.generate_content(
                prompt
            )

            answer = response.text

            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )