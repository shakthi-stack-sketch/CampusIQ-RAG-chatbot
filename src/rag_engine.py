import os
import shutil

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    GOOGLE_API_KEY,
    VECTORSTORE_PATH
)

from src.document_loader import load_documents


# ==========================================
# GET EMBEDDINGS
# ==========================================

def get_embeddings():

    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing. "
            "Please check your .env file."
        )

    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )


# ==========================================
# CREATE VECTORSTORE
# ==========================================

def create_vectorstore():

    print("\nLoading college documents...")

    documents = load_documents()

    if not documents:
        raise ValueError(
            "No documents found in data/college_documents."
        )

    print(f"Loaded {len(documents)} document sections.")

    # Split documents into smaller chunks

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = text_splitter.split_documents(documents)

    print(f"Created {len(chunks)} knowledge chunks.")

    # Remove old vectorstore

    if os.path.exists(VECTORSTORE_PATH):

        print("Removing old knowledge base...")

        shutil.rmtree(VECTORSTORE_PATH)


    print("Creating embeddings and knowledge base...")

    embeddings = get_embeddings()


    # Create Chroma vector database

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH
    )


    print("Knowledge base created successfully!")

    return len(documents), len(chunks)


# ==========================================
# ASK QUESTION
# ==========================================

def ask_question(question):

    # Check whether vectorstore exists

    if not os.path.exists(VECTORSTORE_PATH):

        return (
            "⚠️ The CampusIQ knowledge base has not been created yet. "
            "Please build the knowledge base first.",
            []
        )


    try:

        # Load embeddings

        embeddings = get_embeddings()


        # Load existing vector database

        vectorstore = Chroma(
            persist_directory=VECTORSTORE_PATH,
            embedding_function=embeddings
        )


        # Search relevant information

        results = vectorstore.similarity_search(
            question,
            k=4
        )


        # No relevant documents

        if not results:

            return (
                "I couldn't find this information in the available "
                "Prathyusha Engineering College documents.",
                []
            )


        # Combine retrieved information

        context_parts = []

        for doc in results:

            source = doc.metadata.get(
                "source",
                "Unknown Document"
            )

            page = doc.metadata.get(
                "page",
                0
            )

            context_parts.append(
                f"""
SOURCE: {source}
PAGE: {page + 1}

CONTENT:
{doc.page_content}
"""
            )


        context = "\n\n".join(context_parts)


        # ==========================================
        # GEMINI LLM
        # ==========================================

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0
        )


        # ==========================================
        # PROMPT
        # ==========================================

        prompt = f"""
You are CampusIQ, an AI-powered college knowledge assistant
created specifically for Prathyusha Engineering College.

Your job is to help students find accurate information about
Prathyusha Engineering College.

IMPORTANT RULES:

1. Answer ONLY using the information provided below.

2. Do NOT invent information.

3. Do NOT guess missing information.

4. If the answer is not available in the provided information,
say exactly:

"I couldn't find this information in the available Prathyusha
Engineering College documents."

5. Give answers in a clear, friendly and professional manner.

6. Use bullet points when they make the answer easier to read.

7. If the student asks about timings, dates, menus, rules,
academics, hostel facilities, clubs, dress code or campus activities,
carefully use the information available in the retrieved documents.

8. Do not provide information about other colleges.

9. You represent CampusIQ for Prathyusha Engineering College.

----------------------------------------

COLLEGE INFORMATION:

{context}

----------------------------------------

STUDENT QUESTION:

{question}

----------------------------------------

ANSWER:
"""


        # Generate answer

        response = llm.invoke(prompt)


        return response.content, results


    except Exception as e:

        print(f"Error while answering question: {str(e)}")

        return (
            "⚠️ Sorry, CampusIQ is unable to generate an answer right now. "
            "Please try again.",
            []
        )