import streamlit as st
import pydicom
import cv2
import numpy as np
import io

# 1. Page Config for Speed
st.set_page_config(page_title="Fast DICOM", layout="centered")

# 2. Ultra-Fast UI
st.markdown("""
    <style>
    .main { background-color: #000; }
    .stButton>button { 
        background-color: #25D366; color: white; 
        border-radius: 5px; height: 3.5em; width: 100%;
        font-size: 20px; font-weight: bold;
    }
    h1, p { color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("Fast Medical Converter ⚡")

uploaded_files = st.file_uploader("Upload DICOM", accept_multiple_files=True)

if uploaded_files:
    if st.button("CONVERT NOW (FAST)"):
        # Progress bar for better UX
        progress_bar = st.progress(0)
        slices = []
        
        # Sort files to maintain sequence
        files = sorted(uploaded_files, key=lambda x: x.name)
        
        for i, f in enumerate(files):
            try:
                ds = pydicom.dcmread(f)
                img = ds.pixel_array.astype(float)
                # Fast Normalization
                img = ((img - np.min(img)) / (np.max(img) - np.min(img)) * 255).astype(np.uint8)
                img = cv2.resize(img, (512, 512))
                img_bgr = cv2.merge([img, img, img])
                slices.append(img_bgr)
                progress_bar.progress((i + 1) / len(files))
            except:
                continue

        if slices:
            # Create video in a temporary path for maximum speed
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
                output_path = tmp.name
                
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, 15, (512, 512))
            
            for s in slices:
                out.write(s)
            out.release()

            # Read for download
            with open(output_path, "rb") as f:
                data = f.read()

            st.success("Lightning Fast Conversion Done!")
            st.download_button(
                label="📥 DOWNLOAD MP4",
                data=data,
                file_name="Fast_Scan.mp4",
                mime="video/mp4"
            )
