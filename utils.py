import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from typing import Tuple, List
import streamlit as st

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

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings using SequenceMatcher with preprocessing.
    Returns a value between 0 (completely different) and 1 (identical).
    """
    # Preprocess both strings
    processed_str1 = preprocess_text(str1)
    processed_str2 = preprocess_text(str2)
    
    # Handle empty strings
    if not processed_str1 and not processed_str2:
        return 1.0
    if not processed_str1 or not processed_str2:
        return 0.0
    
    # Calculate similarity using SequenceMatcher
    base_similarity = SequenceMatcher(None, processed_str1, processed_str2).ratio()
    
    # Check for partial matches
    if processed_str1 in processed_str2 or processed_str2 in processed_str1:
        # Boost similarity for partial matches
        return min(1.0, base_similarity + 0.2)
    
    return base_similarity

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
