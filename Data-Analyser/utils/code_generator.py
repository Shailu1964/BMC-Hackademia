import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'AIzaSyB2gpkalAryQCj3tvfZrLJT4c5AcKCpHQ4'))

def clean_code(code):
    """Clean up the generated code and ensure proper imports."""
    # Remove markdown formatting
    if code.startswith('```python'):
        code = code.replace('```python', '').replace('```', '')
    if code.startswith('Here'):
        code = code.split('\n', 1)[1]
    
    code = code.strip()
    
    # Remove any attempts to read CSV files
    lines = code.split('\n')
    cleaned_lines = [line for line in lines if 'read_csv' not in line]
    code = '\n'.join(cleaned_lines)
    
    # Check if code contains visualization but missing import
    if 'create_plot' in code and 'from utils.visualization import create_plot' not in code:
        code = 'from utils.visualization import create_plot\n' + code
    
    # Ensure pandas and numpy imports if needed
    if ('pd.' in code or 'DataFrame' in code) and 'import pandas as pd' not in code:
        code = 'import pandas as pd\n' + code
    if 'np.' in code and 'import numpy as np' not in code:
        code = 'import numpy as np\n' + code
    
    return code

def generate_pandas_code(question, columns, include_viz=True):
    """Generate pandas code using Google's Gemini API based on user question and available columns."""
    
    viz_hint = """
    For visualization requests:
    - Always include 'from utils.visualization import create_plot' when using create_plot
    - Available plot types: line, scatter, bar, histogram, boxplot, heatmap, pie
    - Example: result = create_plot('line', data=df, x='column1', y='column2', title='Trend')
    - The DataFrame 'df' is already loaded and available
    """
    
    prompt = f"""Generate ONLY Python code (no explanations) to analyze this dataset with columns: {', '.join(columns)}
    Question: "{question}"
    
    CRITICAL RULES:
    1. ALWAYS include required imports at the top (pandas, numpy, create_plot)
    2. The DataFrame 'df' is already loaded - DO NOT use read_csv
    3. Store final result in 'result' variable
    4. Format numbers with f-strings and commas
    5. NO comments or markdown
    6. Keep code concise
    7. The code should be directly executable - No samples or examples
    8. If user asks general questions , reply with correct general output as a python string. (for example - user:"hi how are you", python_code(ouput): result = "am fine how are you ")
    9. Also make sure there are interactive text along with the answers and tables.
    {viz_hint if include_viz else ''}
    """
    
    # Configure generation parameters
    generation_config = GenerationConfig(
        temperature=0.5,  # Lower temperature for more consistent outputs
        top_p=0.8,       # Nucleus sampling parameter
        max_output_tokens=500,  # Maximum length of response
        candidate_count=1  # Number of completion choices to generate
    )
    
    # Generate code using Gemini with configuration
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(
        prompt,
        generation_config=generation_config
    )
    
    # Clean up the generated code
    return clean_code(response.text.strip())
