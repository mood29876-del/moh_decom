import streamlit as st
import pydicom
import cv2
import numpy as np
import os
import tempfile

# 1. Page Settings
st.set_page_config(page_title="DICOM Fast Converter", layout="centered")

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
    </style>
    """, unsafe_allow_html=True)

st.title("Medical DICOM Converter (High Speed)")
st.write("Upload DCM files. Processing is optimized for speed using XVID.")

# 3. File Uploader
uploaded_files = st.file_uploader("Select DICOM Files", accept_multiple_files=True)

if uploaded_files:
    if st.button("PROCESS AND CONVERT"):
        with st.spinner("Processing with XVID..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                slices = []
                
                for f in uploaded_files:
                    try:
                        ds = pydicom.dcmread(f)
                        img = ds.pixel_array.astype(float)
                        img = (np.maximum(img, 0) / img.max()) * 255.0
                        img = np.uint8(img)
                        # Standard medical size for speed
                        img = cv2.resize(img, (512, 512))
                        slices.append(img)
                    except Exception as e:
                        st.error(f"Error reading {f.name}")

                if slices:
                    output_path = os.path.join(tmpdir, "output_video.avi")
                    
                    # --- Optimized XVID Settings ---
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    # fps=10 for smooth viewing
                    out = cv2.VideoWriter(output_path, fourcc, 10, (512, 512), False)
                    
                    for s in slices:
                        out.write(s)
                    out.release()
                    
                    # 4. Download Button
                    with open(output_path, "rb") as vid:
                        st.download_button(
                            label="DOWNLOAD VIDEO (XVID)",
                            data=vid,
                            file_name="medical_result.avi",
                            mime="video/x-msvideo"
                        )
                    st.success("Fast Conversion Complete!")
