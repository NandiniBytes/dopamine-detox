# Service for Retrieval-Augmented Generation using FAISS.

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from app.services.llm_service import get_llm_completion
from typing import List

# --- Global variables for the RAG service ---
# In a larger app, this might be a class, but globals are fine for this scope.
model = None
index = None
documents = []
INDEX_PATH = "faiss_index.bin"
KNOWLEDGE_BASE_PATH = "data/knowledge_base"

def initialize_rag_service():
    """
    Initializes the RAG model, loads documents, and builds the FAISS index.
    This should be called at application startup.
    """
    global model, index, documents
    
    print("INFO:     Initializing RAG service...")
    # 1. Load the sentence transformer model
    # This model is great for creating numerical representations (embeddings) of text.
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # 2. Load or build the FAISS index
    if os.path.exists(INDEX_PATH):
        print(f"INFO:     Loading existing FAISS index from {INDEX_PATH}")
        index = faiss.read_index(INDEX_PATH)
        # Also need to load the documents that correspond to the index
        # For simplicity, we'll just reload them from the source. A more robust
        # system would save the document list with the index.
        _load_documents()
    else:
        print("INFO:     No FAISS index found. Building a new one.")
        _load_documents()
        _build_and_save_index()
    
    print(f"INFO:     RAG service initialized with {len(documents)} document chunks.")

def _load_documents():
    """Loads text from files in the knowledge base directory."""
    global documents
    documents = []
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        print(f"WARNING:  Knowledge base directory not found at {KNOWLEDGE_BASE_PATH}. RAG will have no data.")
        os.makedirs(KNOWLEDGE_BASE_PATH)
        # Create dummy files for demonstration
        with open(os.path.join(KNOWLEDGE_BASE_PATH, "minimalism.md"), "w") as f:
            f.write("Minimalism is a lifestyle that helps people question what things add value to their lives. By clearing the clutter from life’s path, we can all make room for the most important aspects of life: health, relationships, passion, growth, and contribution.")
        with open(os.path.join(KNOWLEDGE_BASE_PATH, "digital_wellbeing.md"), "w") as f:
            f.write("Digital wellbeing focuses on creating and maintaining a healthy relationship with technology. Key practices include setting screen time limits, curating your information diet, and scheduling regular 'digital detox' periods to reconnect with the offline world.")

    for filename in os.listdir(KNOWLEDGE_BASE_PATH):
        if filename.endswith((".md", ".txt")):
            with open(os.path.join(KNOWLEDGE_BASE_PATH, filename), 'r', encoding='utf-8') as f:
                # Simple chunking: treat each file as a single document.
                # A more advanced system would split large files into paragraphs.
                documents.append(f.read())

def _build_and_save_index():
    """Creates embeddings and builds/saves the FAISS index."""
    global index
    if not documents:
        print("WARNING:  No documents to index.")
        return

    # 3. Create embeddings for all documents
    print("INFO:     Creating embeddings for documents...")
    embeddings = model.encode(documents, convert_to_tensor=False)
    
    # 4. Build the FAISS index
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)  # Using a simple L2 distance index
    index.add(embeddings)
    
    # 5. Save the index to disk for persistence
    print(f"INFO:     Saving FAISS index to {INDEX_PATH}")
    faiss.write_index(index, INDEX_PATH)

def search_documents(query: str, k: int = 3) -> List[str]:
    """
    Searches the FAISS index for the most relevant document chunks.
    """
    if not index or not documents:
        return []
    
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, k)
    
    # Return the text of the top k documents
    return [documents[i] for i in indices[0]]

def query_rag(query: str) -> str:
    """
    Performs a RAG query: retrieves relevant docs and generates an answer.
    """
    print(f"INFO:     Performing RAG query for: '{query}'")
    # 1. Retrieve relevant context
    retrieved_docs = search_documents(query)
    
    if not retrieved_docs:
        return "I couldn't find any information on that topic in my knowledge base."

    context = "\n\n---\n\n".join(retrieved_docs)
    
    # 2. Build the prompt for the LLM
    prompt = f"""
    You are an expert on digital wellbeing and minimalism. Answer the user's question based *only* on the provided context.
    If the context doesn't contain the answer, say so. Do not use outside knowledge.

    CONTEXT:
    {context}

    QUESTION:
    {query}

    ANSWER:
    """
    
    # 3. Generate the final answer
    return get_llm_completion(prompt, max_tokens=512)
