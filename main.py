import streamlit as st
import pandas as pd
import plotly.express as px
from utils import process_excel_file, get_summary_stats, validate_file_upload
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Excel Column Similarity Analyzer",
    page_icon="📊",
    layout="wide"
)

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
    # Header
    st.title("📊 Excel Column Similarity Analyzer")
    st.markdown("Upload an Excel file and analyze similarity between columns")
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Validate file
        is_valid, message = validate_file_upload(uploaded_file)
        
        if not is_valid:
            st.error(message)
            return
        
        try:
            df = pd.read_excel(uploaded_file)
            
            # Display data preview
            st.markdown("### Data Preview")
            st.dataframe(df.head())
            
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
                
                # Display results section
                st.markdown('<div class="results-section">', unsafe_allow_html=True)
                
                # Summary statistics
                st.markdown("### 📈 Summary Statistics")
                stats = get_summary_stats(similarity_scores)
                
                # Display stats in columns
                cols = st.columns(len(stats))
                for col, (metric, value) in zip(cols, stats.items()):
                    col.metric(metric, value)
                
                # Visualizations
                st.markdown("### 📊 Similarity Analysis")
                
                # Create tabs for different visualizations
                tab1, tab2 = st.tabs(["Distribution", "Scatter Plot"])
                
                with tab1:
                    # Histogram
                    fig_hist = px.histogram(
                        processed_df,
                        x="Similarity_Score",
                        nbins=20,
                        title="Distribution of Similarity Scores",
                        labels={"Similarity_Score": "Similarity Score", "count": "Frequency"},
                        color_discrete_sequence=['#FF4B4B']
                    )
                    fig_hist.update_layout(bargap=0.2)
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                with tab2:
                    # Scatter plot of values
                    fig_scatter = px.scatter(
                        processed_df,
                        x=first_column,
                        y=second_column,
                        color="Similarity_Score",
                        title=f"Value Comparison with Similarity Scores",
                        color_continuous_scale="RdYlBu",
                        hover_data=[first_column, second_column, "Similarity_Score"]
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Add threshold filter
                threshold = st.slider(
                    "Filter by Similarity Score",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.1
                )
                
                filtered_df = processed_df[processed_df["Similarity_Score"] >= threshold]
                
                # Results table
                st.markdown("### 📋 Detailed Results")
                st.markdown(f"Showing {len(filtered_df)} rows with similarity score >= {threshold:.1f}")
                st.dataframe(
                    filtered_df.style.background_gradient(
                        subset=["Similarity_Score"],
                        cmap="RdYlBu",
                        vmin=0,
                        vmax=1
                    )
                )
                
                # Download button
                st.markdown("### 💾 Download Results")
                st.markdown(get_download_link(processed_df), unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
