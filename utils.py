import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from typing import Tuple, List
import streamlit as st

def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings using SequenceMatcher.
    """
    if pd.isna(str1) or pd.isna(str2):
        return 0.0
    
    str1 = str(str1).lower().strip()
    str2 = str(str2).lower().strip()
    
    return SequenceMatcher(None, str1, str2).ratio()

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
