import streamlit as st
import pandas as pd
import os
import zipfile
from pathlib import Path

# Set up Streamlit configuration
st.set_page_config(page_title="Image Review and Selection", layout="wide")

# Define the UI layout
st.title("Image Review and Selection")

# Sidebar for file uploads and settings
with st.sidebar:
    st.header("Upload Files")
    zip_file = st.file_uploader("Upload ZIP File Containing Images", type=["zip"])
    csv_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    # Slider to control image width
    image_width = st.slider("Adjust Image Width", min_value=100, max_value=1000, value=500, key="image_width_slider")
    
    # Placeholder for Predicted Label Column selectbox
    pred_label_col = None
    if 'df' in st.session_state:
        pred_label_col = st.selectbox(
            "Select Predicted Label Column:",
            options=st.session_state.df.columns,
            key="pred_label_col_sidebar"
        )
    
    # Button to save progress
    if st.button("Save Progress", key="save_progress_sidebar"):
        if 'df' in st.session_state:
            csv_download = st.session_state.df.to_csv(index=False)
            st.download_button(
                label="Download Progress CSV",
                data=csv_download,
                file_name="progress.csv",
                mime="text/csv",
                key="download_progress_sidebar"
            )
        else:
            st.warning("No data to save. Please upload a CSV file and start reviewing.")
    
    # Download updated CSV
    if st.button("Download Final CSV File", key="download_final_sidebar"):
        if 'df' in st.session_state:
            csv_download = st.session_state.df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_download,
                file_name="updated_csv_file.csv",
                mime="text/csv",
                key="download_final_button_sidebar"
            )
        else:
            st.warning("No data to download. Please upload a CSV file and start reviewing.")

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
    if 'result' not in df.columns:
        df['result'] = "Pass"
    if 'fail_reason' not in df.columns:
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
        st.image(image_path, width=image_width)
    else:
        st.error("Image not found!")
    
    # Ensure Predicted Label Column is selected
    if pred_label_col:
        pred_label = df.iloc[index][pred_label_col]
        if pred_label == 1:
            label_text = "A"
        elif pred_label == 2:
            label_text = "B"
        elif pred_label == 3:
            label_text = "C"
        else:
            label_text = str(pred_label)
        
        st.write(f"Predicted Label: {label_text}")
    else:
        st.warning("Please select the Predicted Label Column from the sidebar.")
        label_text = "N/A"
    
    # Choose result
    decision = st.radio(
        "Choose Result:",
        ("Pass", "Fail"),
        index=0 if df.iloc[index]['result'] == "Pass" else 1,
        key="decision"
    )
    
    # If "Fail", provide a reason
    fail_reason = None
    if decision == "Fail":
        fail_reason = st.text_input(
            "Enter Reason for Fail:",
            value=df.iloc[index]['fail_reason'],
            key="fail_reason"
        )
    
    # Update the DataFrame with the user's input
    df.at[index, 'result'] = decision
    df.at[index, 'fail_reason'] = fail_reason
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    if col1.button("Previous Image", key="prev_image"):
        if index > 0:
            st.session_state.index -= 1
        else:
            st.warning("You are at the first image.")
    
    if col3.button("Next Image", key="next_image"):
        if index < len(df) - 1:
            st.session_state.index += 1
        else:
            st.warning("You are at the last image.")
    
    # Progress bar
    st.progress((index + 1) / len(df))
