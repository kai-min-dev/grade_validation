import streamlit as st
import pandas as pd
import os
from PIL import Image
from zipfile import ZipFile

# Set up Streamlit configuration
st.set_page_config(page_title="Image Review and Selection", layout="wide")

# Define the UI layout
st.title("Image Review and Selection")

# Caching functions to improve performance
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

@st.cache_data
def load_image(image_path, width=400):
    image = Image.open(image_path)
    resized_image = image.resize((width, int(image.height * width / image.width)))
    return resized_image

@st.cache_data
def extract_image(zip_file_path, image_name):
    with ZipFile(zip_file_path, 'r') as zip_ref:
        image_data = zip_ref.read(image_name)
    return Image.open(io.BytesIO(image_data))

# Sidebar for file uploads and settings
with st.sidebar:
    st.header("Upload Files")
    zip_file = st.file_uploader("Upload ZIP File Containing Images", type=["zip"])
    csv_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    # Predicted Label Column selectbox with search functionality
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

# Initialize lists in session state to store decisions and fail reasons
if 'decision' not in st.session_state:
    st.session_state.decision = []

if 'fail_reason' not in st.session_state:
    st.session_state.fail_reason = []

# Ensure lists are the correct length
if 'df' in st.session_state:
    while len(st.session_state.decision) < len(st.session_state.df):
        st.session_state.decision.append("Pass")
        st.session_state.fail_reason.append(None)

# Extract ZIP file and load images
if zip_file:
    with ZipFile(zip_file, 'r') as zip_ref:
        image_files = zip_ref.namelist()
        st.session_state.img_folder = zip_file.name

# Load CSV file
if csv_file:
    df = load_data(csv_file)
    if 'result' not in df.columns:
        df['result'] = "Pass"
    if 'fail_reason' not in df.columns:
        df['fail_reason'] = None
    st.session_state.df = df

    # Ensure lists in session state match the dataframe
    st.session_state.decision = df['result'].tolist()
    st.session_state.fail_reason = df['fail_reason'].tolist()

# Display the current image
if 'df' in st.session_state and 'img_folder' in st.session_state:
    df = st.session_state.df
    index = st.session_state.index
    
    # Display the sequence name
    st.subheader(f"Sequence: {df.iloc[index]['Sequence']}")
    
    # Display current progress (e.g., "Image 5 of 20")
    st.text(f"Image {index + 1} of {len(df)}")

    # Find and display the image
    sequence_name = df.iloc[index]['Sequence']
    image_path = None
    
    # Look for the image in the extracted files
    for file_name in image_files:
        if sequence_name in file_name:
            image_path = os.path.join(st.session_state.img_folder, file_name)
            break
    
    if image_path:
        image = load_image(image_path)
        st.image(image)
    else:
        st.error("Image not found!")
    
    # Ensure Predicted Label Column is selected
    if 'pred_label_col_sidebar' in st.session_state:
        pred_label_col = st.session_state.pred_label_col_sidebar
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
    
    # Choose result with saved or default value
    decision = st.radio(
        "Choose Result:",
        ("Pass", "Fail"),
        index=0 if st.session_state.decision[index] == "Pass" else 1,
        key="decision_radio"
    )
    
    # If "Fail", provide a reason with saved or default value
    fail_reason = None
    if decision == "Fail":
        fail_reason = st.text_input(
            "Enter Reason for Fail:",
            value=st.session_state.fail_reason[index] if st.session_state.fail_reason[index] is not None else "",
            key="fail_reason_input"
        )
    
    # Save user selection in session state
    st.session_state.decision[index] = decision
    st.session_state.fail_reason[index] = fail_reason
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    if col1.button("Previous Image", key="prev_image"):
        if index > 0:
            st.session_state.index -= 1
    
    if col3.button("Next Image", key="next_image"):
        if index < len(df) - 1:
            st.session_state.index += 1

    # Progress bar
    st.progress((index + 1) / len(df))
