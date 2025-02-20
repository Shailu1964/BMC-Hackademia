import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import pandas as pd
import numpy as np

def create_plot(plot_type, data, x=None, y=None, title=None, kind='line', figsize=(10, 6)):
    """Create different types of plots based on the plot type and data."""
    plt.figure(figsize=figsize)
    plt.style.use('dark_background')
    
    if plot_type == 'line':
        plt.plot(data[x], data[y])
    elif plot_type == 'scatter':
        plt.scatter(data[x], data[y])
    elif plot_type == 'bar':
        if y is not None:
            # If both x and y are provided, create a bar plot with actual y values
            sns.barplot(x=x, y=y, data=data)
        else:
            # If only x is provided, create a count-based bar plot
            data[x].value_counts().plot(kind='bar')
    elif plot_type == 'histogram':
        plt.hist(data[x], bins=30)
    elif plot_type == 'boxplot':
        sns.boxplot(x=x, y=y, data=data)
    elif plot_type == 'heatmap':
        if isinstance(data, (pd.DataFrame, np.ndarray)):
            sns.heatmap(data, annot=True, cmap='coolwarm')
        else:
            sns.heatmap(data.corr(), annot=True, cmap='coolwarm')
    elif plot_type == 'pie':
        data[x].value_counts().plot(kind='pie', autopct='%1.1f%%')
    
    if title:
        plt.title(title)
        
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300, facecolor='#0e1117')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return image_base64

def get_numeric_columns(df):
    """Get list of numeric columns from dataframe."""
    return df.select_dtypes(include=['int64', 'float64']).columns.tolist()

def get_categorical_columns(df):
    """Get list of categorical columns from dataframe."""
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def suggest_plots(df):
    """Suggest suitable plots based on data types."""
    numeric_cols = get_numeric_columns(df)
    categorical_cols = get_categorical_columns(df)
    
    suggestions = []
    
    if len(numeric_cols) >= 2:
        suggestions.append({
            'type': 'scatter',
            'description': f"Create a scatter plot between {numeric_cols[0]} and {numeric_cols[1]}",
            'x': numeric_cols[0],
            'y': numeric_cols[1]
        })
        
        suggestions.append({
            'type': 'line',
            'description': f"Show trend line for {numeric_cols[0]}",
            'x': df.index.name or 'index',
            'y': numeric_cols[0]
        })
    
    if len(numeric_cols) > 0:
        suggestions.append({
            'type': 'histogram',
            'description': f"Show distribution of {numeric_cols[0]}",
            'x': numeric_cols[0]
        })
        
        suggestions.append({
            'type': 'boxplot',
            'description': f"Show boxplot for {numeric_cols[0]}",
            'x': numeric_cols[0]
        })
    
    if len(categorical_cols) > 0:
        suggestions.append({
            'type': 'bar',
            'description': f"Show counts for {categorical_cols[0]}",
            'x': categorical_cols[0]
        })
        
        suggestions.append({
            'type': 'pie',
            'description': f"Show percentage distribution of {categorical_cols[0]}",
            'x': categorical_cols[0]
        })
    
    if len(numeric_cols) > 3:
        suggestions.append({
            'type': 'heatmap',
            'description': "Show correlation heatmap for numeric columns"
        })
    
    return suggestions
