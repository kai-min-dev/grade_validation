import streamlit as st
import pandas as pd
import os
import zipfile
from pathlib import Path

# Set up Streamlit configuration
st.set_page_config(page_title="Image Review and Selection", layout="wide")

# Define the UI layout
st.title("Image Review and Selection")

# Sidebar for file uploads
with st.sidebar:
    st.header("Upload Files")
    zip_file = st.file_uploader("Upload ZIP File Containing Images", type=["zip"])
    csv_file = st.file_uploader("Upload CSV File", type=["csv"])
    
# Initialize session state
if 'index' not in st.session_state:
    st.session_state.index = 0

# Extract ZIP file and load images
if zip_file:
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("extracted_images")
    st.session_state.img_folder = "extracted_images"

# Load CSV file
if csv_file:
    df = pd.read_csv(csv_file)
    df['result'] = "Pass"
    df['fail_reason'] = None
    st.session_state.df = df

# Display the current image
if 'df' in st.session_state and 'img_folder' in st.session_state:
    df = st.session_state.df
    index = st.session_state.index
    
    # Display the sequence name
    st.subheader(f"Sequence: {df.iloc[index]['Sequence']}")
    
    # Find and display the image
    sequence_name = df.iloc[index]['Sequence']
    image_path = None
    for root, dirs, files in os.walk(st.session_state.img_folder):
        if sequence_name in files:
            image_path = os.path.join(root, sequence_name)
            break
    
    if image_path:
        st.image(image_path, use_column_width=True)
    else:
        st.error("Image not found!")
    
    # Display the predicted label
    pred_label_col = st.selectbox("Select Predicted Label Column:", df.columns, key="pred_label_col")
    st.write(f"Predicted Label: {df.iloc[index][pred_label_col]}")

    # Choose result
    decision = st.radio("Choose Result:", ("Pass", "Fail"), index=0 if df.iloc[index]['result'] == "Pass" else 1, key="decision")
    
    # If "Fail", provide a reason
    fail_reason = None
    if decision == "Fail":
        fail_reason = st.text_input("Enter Reason for Fail:", value=df.iloc[index]['fail_reason'])
    
    # Update the DataFrame with the user's input
    df.at[index, 'result'] = decision
    df.at[index, 'fail_reason'] = fail_reason
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    if col1.button("Previous Image") and index > 0:
        st.session_state.index -= 1
    
    if col3.button("Next Image") and index < len(df) - 1:
        st.session_state.index += 1
    
    # Progress bar
    st.progress((index + 1) / len(df))
    
    # Download updated CSV
    if st.button("Download CSV File"):
        csv_download = df.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv_download, file_name="updated_csv_file.csv", mime="text/csv")

# To run this app locally:
# 1. Save this code in a file named `app.py`.
# 2. Install Streamlit with `pip install streamlit`.
# 3. Run the app using `streamlit run app.py`.
