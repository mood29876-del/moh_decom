import streamlit as st
import pydicom
import cv2
import numpy as np
import os
import tempfile

# 1. Page Settings
st.set_page_config(page_title="DICOM to MP4 Professional", layout="centered")

# 2. Professional Dark Theme (CSS)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    body { color: #ffffff; background-color: #000000; }
    .stButton>button { 
        background-color: #1a1a1a; 
        color: #00ff00; 
        border: 1px solid #333; 
        border-radius: 5px; 
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover { border: 1px solid #00ff00; color: #ffffff; }
    h1, p, label { color: #ffffff !important; }
    .uploadedFile { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

st.title("Medical DICOM Converter")
st.write("Upload your DCM files to generate a high-speed MP4 video.")

# 3. File Uploader
uploaded_files = st.file_uploader("Select DICOM Files", accept_multiple_files=True)

if uploaded_files:
    if st.button("PROCESS AND CONVERT"):
        with st.spinner("Converting..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                slices = []
                
                # Processing each file
                for f in uploaded_files:
                    try:
                        ds = pydicom.dcmread(f)
                        img = ds.pixel_array.astype(float)
                        
                        # Rescaling pixel values
                        img = (np.maximum(img, 0) / img.max()) * 255.0
                        img = np.uint8(img)
                        
                        # Resize to 512x512 for better performance on Render
                        img = cv2.resize(img, (512, 512))
                        slices.append(img)
                    except Exception as e:
                        st.error(f"Error in file {f.name}")

                if slices:
                    output_path = os.path.join(tmpdir, "output_video.mp4")
                    
                    # Using XVID codec for speed and compatibility
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    
                    # FPS is set to 10 for balanced speed
                    out = cv2.VideoWriter(output_path, communities=fourcc, fps=10, frameSize=(512, 512), isColor=False)
                    
                    for s in slices:
                        out.write(s)
                    out.release()
                    
                    # 4. Download Button
                    with open(output_path, "rb") as vid:
                        st.download_button(
                            label="DOWNLOAD MP4 VIDEO",
                            data=vid,
                            file_name="doctor_view.mp4",
                            mime="video/mp4"
                        )
                    st.success("Conversion Successful!")
