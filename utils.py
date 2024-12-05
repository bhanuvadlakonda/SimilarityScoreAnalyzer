import pandas as pd
import numpy as np
from typing import Tuple, List
import streamlit as st
from sentence_transformers import SentenceTransformer, util
import torch

def preprocess_text(text: str) -> str:
    """
    Preprocess text for comparison by normalizing format.
    """
    if pd.isna(text):
        return ""
    
    # Convert to string and lowercase
    text = str(text).lower()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters (keeping alphanumeric and spaces)
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    
    return text.strip()

from sentence_transformers import SentenceTransformer
import torch

# Initialize the model (this will be done only once)
@st.cache_resource
def get_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate semantic similarity between two strings using sentence transformers.
    Returns a value between 0 (completely different) and 1 (most similar).
    """
    if pd.isna(str1) or pd.isna(str2):
        return 0.0
    
    # Convert to string
    str1 = str(str1).strip()
    str2 = str(str2).strip()
    
    # Handle empty strings
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0
    
    try:
        # Get model
        model = get_model()
        
        # Encode sentences to get embeddings
        embedding1 = model.encode(str1, convert_to_tensor=True)
        embedding2 = model.encode(str2, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        
        # Normalize to [0,1] range (as cosine similarity is in [-1,1] range)
        normalized_similarity = (similarity + 1) / 2
        
        return float(normalized_similarity)
    except Exception as e:
        st.error(f"Error calculating similarity: {str(e)}")
        return 0.0

def process_excel_file(
    df: pd.DataFrame,
    col1: str,
    col2: str,
    new_col_name: str = "Similarity_Score"
) -> Tuple[pd.DataFrame, List[float]]:
    """
    Calculate similarity scores between two columns and add results to dataframe.
    """
    # Calculate similarity scores
    similarity_scores = [
        calculate_similarity(str1, str2)
        for str1, str2 in zip(df[col1], df[col2])
    ]
    
    # Add scores to dataframe
    df[new_col_name] = similarity_scores
    
    return df, similarity_scores

def get_summary_stats(scores: List[float]) -> dict:
    """
    Calculate summary statistics for similarity scores.
    """
    return {
        "Average Similarity": f"{np.mean(scores):.2%}",
        "Median Similarity": f"{np.median(scores):.2%}",
        "Min Similarity": f"{np.min(scores):.2%}",
        "Max Similarity": f"{np.max(scores):.2%}"
    }

def validate_file_upload(uploaded_file) -> Tuple[bool, str]:
    """
    Validate the uploaded Excel file.
    """
    if uploaded_file is None:
        return False, "Please upload an Excel file"
    
    if not uploaded_file.name.endswith(('.xlsx', '.xls')):
        return False, "Please upload a valid Excel file (.xlsx or .xls)"
    
    return True, "File validated successfully"
