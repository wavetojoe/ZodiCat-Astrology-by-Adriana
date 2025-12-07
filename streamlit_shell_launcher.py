#!/usr/bin/env python3
"""
Streamlit Shell Launcher for PDF Generation
This script provides a Streamlit interface to launch the shell script for PDF generation.
"""

import streamlit as st
import subprocess
import os
import tempfile
import time

st.set_page_config(page_title="PDF Cover Generator", page_icon="🔮", layout="centered")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #9370db75;
        color: #FAFAFA;
    }
    [data-testid="stHeader"] {
        background-color: #9370db75;
    }
    div.stButton > button {
        background-color: #9370DB !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        height: 3em !important;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #8A2BE2 !important;
        transform: scale(1.02);
        box-shadow: 0 0 10px #9370DB;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("PDF Cover Generator")
st.markdown("This tool generates PDF covers using InDesign without resetting the app.")

# Form
with st.form("pdf_form"):
    name = st.text_input("Name", "John Doe")
    
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Birth Date")
    with col2:
        birth_time = st.time_input("Birth Time")
    
    location = st.text_input("Location", "New York, NY, USA")
    
    submit = st.form_submit_button("Generate PDF Covers")

# Handle form submission
if submit:
    # Format birth info
    birth_date_str = birth_date.strftime("%B %d, %Y")
    birth_time_str = birth_time.strftime("%I:%M %p").lstrip('0')
    birth_info = f"{birth_date_str} - {birth_time_str}"
    
    # Create a progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Update status
    status_text.info("Starting PDF generation process...")
    progress_bar.progress(10)
    time.sleep(0.5)
    
    # Get script path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    shell_script = os.path.join(script_dir, "generate_pdfs.sh")
    
    # Update status
    status_text.info("Preparing to run shell script...")
    progress_bar.progress(20)
    time.sleep(0.5)
    
    try:
        # Create a temporary file to capture output
        with tempfile.NamedTemporaryFile(delete=False, mode='w+t') as temp:
            temp_path = temp.name
            
            # Update status
            status_text.info("Launching shell script...")
            progress_bar.progress(30)
            
            # Start the process
            cmd = [
                shell_script,
                "--name", name,
                "--birth-info", birth_info,
                "--location", location
            ]
            
            # Run the command and capture output
            process = subprocess.Popen(
                cmd, 
                stdout=temp,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Update status while waiting for process to complete
            status_text.info("Generating PDFs with InDesign... This may take a moment.")
            progress_bar.progress(50)
            
            # Wait for process to complete
            process.wait()
            
            # Update progress
            progress_bar.progress(90)
            status_text.info("Processing results...")
            time.sleep(0.5)
            
            # Read the output
            temp.flush()
            temp.close()
            with open(temp_path, 'r') as f:
                output = f.read()
            
            # Clean up
            os.unlink(temp_path)
            
            # Check result
            if process.returncode == 0:
                progress_bar.progress(100)
                status_text.success("PDF covers generated successfully!")
                
                # Extract output folder from the output
                output_folder = None
                for line in output.split('\n'):
                    if "Output folder:" in line:
                        output_folder = line.split("Output folder:")[1].strip()
                        break
                
                if output_folder:
                    st.success(f"PDF covers saved to: {output_folder}")
                
                # Display the output
                with st.expander("View Process Output"):
                    st.code(output)
            else:
                progress_bar.progress(100)
                status_text.error("Error generating PDF covers")
                st.error("The PDF generation process failed.")
                st.code(output)
    
    except Exception as e:
        progress_bar.progress(100)
        status_text.error("Error occurred")
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
