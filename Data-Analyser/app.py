import streamlit as st
import pandas as pd
import numpy as np

from styles.main import get_css
from utils.code_generator import generate_pandas_code
from src.components import (
    render_column_list,
    render_dataset_info,
    render_dataset_preview,
    render_plot_suggestions,
    display_result
)

def main():
    # Set page config for full width
    st.set_page_config(
        page_title="Data Analyzer",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Apply CSS
    st.markdown(get_css(), unsafe_allow_html=True)
    
    # App header
    st.markdown("# 📊 CSV Data Analyzer")
    st.markdown("Upload your CSV file and ask questions about your data using natural language!")

    # File upload section
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        try:
            # Read the CSV file
            df = pd.read_csv(uploaded_file)
            
            # Create main layout with columns
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Render column list and dataset info
                render_column_list(df)
                render_dataset_info(df)
            
            with col2:
                # Render dataset preview
                render_dataset_preview(df)
                
                # Render plot suggestions
                render_plot_suggestions(df)
                
                # Question input section
                st.markdown("### Ask Questions About Your Data")
                question = st.text_input(
                    "What would you like to know about your data?",
                    placeholder="e.g., 'Show me a scatter plot of column1 vs column2' or 'Calculate the average of column1'"
                )
            
                if question:
                    with st.spinner("Analyzing..."):
                        generated_code = generate_pandas_code(question, list(df.columns))
                        
                        if generated_code:
                            try:
                                # Create namespace with imports
                                namespace = {
                                    'df': df,
                                    'pd': pd,
                                    'np': np,
                                    'result': None
                                }
                                
                                try:
                                    # Clean and execute code
                                    clean_code = '\n'.join(
                                        line for line in generated_code.split('\n')
                                        if line.strip() and not line.strip().startswith('#')
                                    )
                                    exec(clean_code, namespace)
                                    
                                    # Display results
                                    display_result(namespace.get('result'))
                                    
                                except Exception as e:
                                    st.error(f"Error executing code: {str(e)}")
                                    st.error("Please try rephrasing your question.")
                            
                            except Exception as e:
                                st.error(f"Error analyzing data: {str(e)}")
                                st.error("Please try rephrasing your question.")
                            
                            # Show generated code in expander
                            with st.expander("Show Generated Code"):
                                st.code(generated_code, language="python")
                                
        except Exception as e:
            st.error(f"Error reading CSV file: {str(e)}")
    else:
        st.info("👆 Upload a CSV file to get started!")

if __name__ == "__main__":
    main()
