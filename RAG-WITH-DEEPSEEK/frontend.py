import streamlit as st
from rag_pipeline import answer_query, retrieve_docs

st.title("AI Lawyer Chatbot")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF", type="pdf", accept_multiple_files=False)

if uploaded_file:
    from vector_database import process_pdf  # Import function from vector_database.py
    faiss_db = process_pdf(uploaded_file)  # Process uploaded PDF and create FAISS index
    st.success(f"File '{uploaded_file.name}' processed successfully!")

    user_query = st.text_area("Enter your prompt:", height=150, placeholder="Ask Anything!")

    if st.button("Ask AI Lawyer"):
        if user_query:
            st.chat_message("user").write(user_query)
            
            retrieved_docs = retrieve_docs(user_query, faiss_db)  # Retrieve relevant docs
            response = answer_query(retrieved_docs, user_query)  # Get AI response
            
            st.chat_message("AI Lawyer").write(response)
        else:
            st.error("Please enter a query!")
else:
    st.warning("Please upload a PDF first.")
