from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from vector_database import get_embedding_model

from dotenv import load_dotenv
load_dotenv()

# LLM Model (Groq API)
LLM_MODEL = ChatGroq(model="deepseek-r1-distill-llama-70b")

# Prompt Template
CUSTOM_PROMPT = """
Use the pieces of information provided in the context to answer the user's question.
If you don't know the answer, just say you don't know—don't make up an answer.
Don't provide anything out of the given context.

Question: {question}
Context: {context}
Answer:
"""

def retrieve_docs(query, faiss_db):
    """Searches the FAISS vector store for similar documents."""
    return faiss_db.similarity_search(query)

def get_context(documents):
    """Extracts the text from retrieved documents."""
    return "\n\n".join([doc.page_content for doc in documents])

def answer_query(documents, query):
    """Generates an answer using the LLM model."""
    context = get_context(documents)
    prompt = ChatPromptTemplate.from_template(CUSTOM_PROMPT)
    chain = prompt | LLM_MODEL
    return chain.invoke({"question": query, "context": context})
