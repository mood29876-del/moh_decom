import streamlit as st
import pydicom
import cv2
import numpy as np
import os
import tempfile

# 1. Page Settings
st.set_page_config(page_title="DICOM to WhatsApp", layout="centered")

# 2. Dark Medical UI
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stButton>button { 
        background-color: #075E54; /* WhatsApp Green */
        color: white; 
        border-radius: 20px; 
        width: 100%;
        font-weight: bold;
    }
    h1, p, label { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("DICOM to MP4 (WhatsApp Ready)")
st.write("Upload DCM files to get a video playable on any mobile phone.")

uploaded_files = st.file_uploader("Select DICOM Files", accept_multiple_files=True)

if uploaded_files:
    if st.button("CONVERT FOR WHATSAPP"):
        with st.spinner("Processing..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                slices = []
                for f in uploaded_files:
                    try:
                        ds = pydicom.dcmread(f)
                        img = ds.pixel_array.astype(float)
                        img = (np.maximum(img, 0) / img.max()) * 255.0
                        img = np.uint8(img)
                        img = cv2.resize(img, (512, 512))
                        # Convert to 3-channel (RGB) for better MP4 compatibility
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                        slices.append(img_rgb)
                    except:
                        continue

                if slices:
                    output_path = os.path.join(tmpdir, "medical_video.mp4")
                    
                    # --- The "Magic" for WhatsApp (H.264 / MP4V) ---
                    # We use 'avc1' or 'mp4v' which are highly compatible
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                    out = cv2.VideoWriter(output_path, fourcc, 10, (512, 512))
                    
                    for s in slices:
                        out.write(s)
                    out.release()
                    
                    with open(output_path, "rb") as vid:
                        st.download_button(
                            label="DOWNLOAD & SEND TO WHATSAPP",
                            data=vid,
                            file_name="patient_scan.mp4",
                            mime="video/mp4"
                        )
                    st.success("Ready for WhatsApp!")
