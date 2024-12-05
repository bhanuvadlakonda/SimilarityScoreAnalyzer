import streamlit as st
import pandas as pd
import plotly.express as px
from utils import process_excel_file, get_summary_stats, validate_file_upload
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Similarity Score Analyzer",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Set dark theme
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1rem;
        }
        div[data-testid="stFileUploader"] {
            border: 1px dashed #30363D;
            border-radius: 0.5rem;
            padding: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Load custom CSS
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def get_download_link(df):
    """Generate a download link for the processed Excel file"""
    towrite = BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="processed_data.xlsx">Download Processed Excel File</a>'

def main():
    st.title("Similarity Score Analyzer")
    st.markdown("Upload your Excel or CSV file and compare data between columns")
    
    # File upload section
    st.markdown("## Upload File")
    st.markdown("Select an Excel (.xlsx) or CSV file to analyze")
    uploaded_file = st.file_uploader("", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file is not None:
        # Validate file
        is_valid, message = validate_file_upload(uploaded_file)
        
        if not is_valid:
            st.error(message)
            return
        
        try:
            df = pd.read_excel(uploaded_file)
            
            if uploaded_file.name:
                st.markdown(f"📊 {uploaded_file.name}")
            
            # Column selection
            cols = df.columns.tolist()
            
            col1, col2 = st.columns(2)
            
            with col1:
                first_column = st.selectbox(
                    "Select first column for comparison",
                    options=cols,
                    key="first_col"
                )
            
            with col2:
                second_column = st.selectbox(
                    "Select second column for comparison",
                    options=cols,
                    key="second_col"
                )
            
            if st.button("Calculate Similarity Scores"):
                if first_column == second_column:
                    st.warning("Please select different columns for comparison")
                    return
                
                # Process data
                processed_df, similarity_scores = process_excel_file(
                    df.copy(),
                    first_column,
                    second_column
                )
                
                # Results section
                st.subheader("Results")
                st.markdown("Similarity scores between selected columns")
                
                # Prepare results dataframe
                results_df = pd.DataFrame({
                    'Column 1': processed_df[first_column],
                    'Column 2': processed_df[second_column],
                    'Similarity Score': [f"{score:.0%}" for score in processed_df['Similarity_Score']]
                })
                
                # Custom styling for the similarity score
                def color_similarity(val):
                    if isinstance(val, str) and val.endswith('%'):
                        return f'<span class="similarity-score">{val}</span>'
                    return val
                
                # Apply custom styling to the dataframe
                st.write(
                    results_df.style
                    .format(lambda x: color_similarity(x))
                    .set_properties(**{
                        'text-align': 'left',
                        'white-space': 'pre-wrap'
                    })
                    .hide(axis='index')
                    .to_html(escape=False),
                    unsafe_allow_html=True
                )
                
                # Download button
                col1, col2 = st.columns([4, 1])
                with col2:
                    st.download_button(
                        label="Download CSV",
                        data=results_df.to_csv(index=False),
                        file_name="similarity_results.csv",
                        mime="text/csv"
                    )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
