import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# Directory to store PDFs
PDFS_DIR = "pdfs/"
os.makedirs(PDFS_DIR, exist_ok=True)

# Embedding model
OLLAMA_MODEL = "deepseek-r1:7b"

def save_pdf(uploaded_file):
    """Saves the uploaded file and returns the file path."""
    file_path = os.path.join(PDFS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def load_pdf(file_path):
    """Loads text from a PDF file."""
    loader = PDFPlumberLoader(file_path)
    return loader.load()

def create_chunks(documents):
    """Splits documents into smaller text chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    return text_splitter.split_documents(documents)

def get_embedding_model():
    """Returns the Ollama embedding model."""
    return OllamaEmbeddings(model=OLLAMA_MODEL)

def build_faiss(text_chunks):
    """Creates a new FAISS vector store."""
    return FAISS.from_documents(text_chunks, get_embedding_model())

def process_pdf(uploaded_file):
    """Handles PDF saving, loading, chunking, and FAISS indexing."""
    file_path = save_pdf(uploaded_file)
    documents = load_pdf(file_path)
    text_chunks = create_chunks(documents)
    return build_faiss(text_chunks)  # Return new FAISS index
