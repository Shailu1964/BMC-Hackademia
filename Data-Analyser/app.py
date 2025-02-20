import streamlit as st
import pandas as pd
import numpy as np

from styles.main import get_css
from utils.code_generator import generate_pandas_code
from utils.preprocessing import fill_null_values, remove_null_rows, normalize_columns, detect_patterns
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

    # Features Overview Section
    with st.expander("✨ Click here to see all available features!", expanded=False):
        st.markdown("""
        ### 🎯 Available Features
        
        #### 1. Data Loading and Preview
        - 📁 Upload any CSV file
        - 📋 View column list and dataset information
        - 🔍 Preview your data instantly
        
        #### 2. Data Preprocessing
        - 🧹 **Fill Missing Values**
          - Fill using mean, median, or zero
          - See before/after statistics
          - Preview processed data
        
        - ❌ **Remove Null Rows**
          - Set custom threshold for removal
          - Track number of rows affected
          - View cleaned dataset preview
        
        - 📊 **Data Normalization**
          - MinMax scaling (0 to 1 range)
          - Standard scaling (mean=0, std=1)
          - Log transformation
          - Compare before/after distributions
        
        - 🔍 **Pattern Detection**
          - Missing value analysis
          - Unique value counts
          - Data type information
          - Correlation analysis with heatmaps
        
        #### 3. Natural Language Analysis
        - 💬 Ask questions about your data in plain English
        - 📈 Get automatic visualizations
        - 🔢 Perform calculations and aggregations
        - 📊 Generate custom plots
        
        #### 4. Export Options
        - 💾 Download preprocessed data as CSV
        - 📥 Save generated plots and analysis
        
        #### How to Use
        1. Upload your CSV file using the upload button below
        2. Use the preprocessing tools in the sidebar to clean and transform your data
        3. Ask questions about your data in the text input
        4. Download your processed data anytime
        """)

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
                
                # Add preprocessing section
                st.markdown("### Data Preprocessing")
                preprocess_expander = st.expander("Preprocessing Options")
                with preprocess_expander:
                    preprocessing_type = st.selectbox(
                        "Select Preprocessing Type",
                        ["Fill Null Values", "Remove Null Rows", "Normalize Data", "Detect Patterns"]
                    )
                    
                    if preprocessing_type == "Fill Null Values":
                        fill_method = st.selectbox("Fill Method", ["mean", "median", "zero"])
                        if st.button("Apply Fill"):
                            original_nulls = df.isnull().sum().sum()
                            df = fill_null_values(df, method=fill_method)
                            remaining_nulls = df.isnull().sum().sum()
                            
                            st.markdown("### Results of Filling Null Values")
                            st.write(f"✨ Successfully filled missing values using the **{fill_method}** method!")
                            st.write(f"📊 Original null count: {original_nulls}")
                            st.write(f"📊 Remaining null count: {remaining_nulls}")
                            st.write(f"🎯 Total values filled: {original_nulls - remaining_nulls}")
                            
                            st.markdown("### Preview of Processed Data")
                            st.dataframe(df.head())
                            
                    elif preprocessing_type == "Remove Null Rows":
                        threshold = st.slider("Null Threshold", 0.0, 1.0, 0.5)
                        if st.button("Remove Nulls"):
                            original_rows = len(df)
                            df = remove_null_rows(df, threshold=threshold)
                            remaining_rows = len(df)
                            
                            st.markdown("### Results of Removing Null Rows")
                            st.write(f"✨ Successfully removed rows with null values!")
                            st.write(f"📊 Original number of rows: {original_rows}")
                            st.write(f"📊 Remaining rows: {remaining_rows}")
                            st.write(f"🎯 Rows removed: {original_rows - remaining_rows}")
                            
                            st.markdown("### Preview of Processed Data")
                            st.dataframe(df.head())
                            
                    elif preprocessing_type == "Normalize Data":
                        norm_method = st.selectbox("Normalization Method", ["minmax", "standard", "log"])
                        numeric_cols = df.select_dtypes(include=[np.number]).columns
                        selected_cols = st.multiselect("Select Columns", numeric_cols, default=list(numeric_cols))
                        
                        if st.button("Normalize"):
                            st.markdown("### Original Data Statistics")
                            st.write("Here are the statistics before normalization:")
                            st.dataframe(df[selected_cols].describe())
                            
                            df = normalize_columns(df, method=norm_method, columns=selected_cols)
                            
                            st.markdown("### Results of Normalization")
                            st.write(f"✨ Successfully normalized data using **{norm_method}** method!")
                            st.write("Here are the statistics after normalization:")
                            st.dataframe(df[selected_cols].describe())
                            
                            # Create before-after distribution plots
                            if len(selected_cols) > 0:
                                st.markdown("### Distribution Visualization")
                                st.write("Here's a visualization of the normalized distributions:")
                                for col in selected_cols[:3]:  # Limit to first 3 columns to avoid cluttering
                                    fig = create_plot('histogram', df, x=col, title=f'Distribution of {col} after {norm_method} normalization')
                                    st.plotly_chart(fig)
                            
                    elif preprocessing_type == "Detect Patterns":
                        if st.button("Analyze Patterns"):
                            patterns = detect_patterns(df)
                            
                            st.markdown("### 📊 Data Pattern Analysis")
                            
                            st.markdown("#### Missing Values Analysis")
                            st.write("Here's the percentage of missing values in each column:")
                            missing_df = pd.DataFrame({
                                'Column': patterns['missing_percentages'].index,
                                'Missing %': patterns['missing_percentages'].values
                            }).sort_values('Missing %', ascending=False)
                            st.dataframe(missing_df)
                            
                            st.markdown("#### Unique Values Count")
                            st.write("Here's the number of unique values in each column:")
                            unique_df = pd.DataFrame({
                                'Column': patterns['unique_counts'].index,
                                'Unique Values': patterns['unique_counts'].values
                            })
                            st.dataframe(unique_df)
                            
                            st.markdown("#### Data Types")
                            st.write("Here are the data types of each column:")
                            dtype_df = pd.DataFrame({
                                'Column': patterns['data_types'].index,
                                'Data Type': patterns['data_types'].values.astype(str)
                            })
                            st.dataframe(dtype_df)
                            
                            st.markdown("#### Correlation Analysis")
                            st.write("Here's the correlation matrix for numeric columns:")
                            fig = create_plot('heatmap', df, data=patterns['numeric_correlations'], 
                                           title='Correlation Matrix')
                            st.plotly_chart(fig)
                    
                    # Download preprocessed data
                    if len(df) > 0:  # Only show download button if we have data
                        st.markdown("### 💾 Download Processed Data")
                        st.write("You can download your processed data as a CSV file:")
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Preprocessed CSV",
                            data=csv,
                            file_name="preprocessed_data.csv",
                            mime="text/csv",
                            help="Click to download the preprocessed dataset"
                        )
            
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
