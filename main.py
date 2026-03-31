import streamlit as st
import pydicom
import cv2
import numpy as np
import os
import tempfile

# 1. Page Configuration
st.set_page_config(page_title="DICOM to MP4 Pro", layout="centered")

# 2. Professional Dark Medical UI (CSS)
st.markdown("""
    <style>
    .main { background-color: #000000; }
    body { color: #ffffff; }
    .stButton>button { 
        background-color: #25D366; 
        color: white; 
        border-radius: 8px; 
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #128C7E; color: white; }
    h1, p, label { color: #ffffff !important; text-align: center; }
    .uploadedFile { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("Medical DICOM Converter ⚕️")
st.write("Convert DICOM slices to WhatsApp-compatible MP4 videos.")

# 3. File Uploader
uploaded_files = st.file_uploader("Upload DCM Files", accept_multiple_files=True)

if uploaded_files:
    if st.button("GENERATE WHATSAPP VIDEO"):
        with st.spinner("Processing medical data..."):
            with tempfile.TemporaryDirectory() as tmpdir:
                slices = []
                
                # Sort files by name to ensure correct video sequence
                uploaded_files.sort(key=lambda x: x.name)

                for f in uploaded_files:
                    try:
                        # Read DICOM
                        ds = pydicom.dcmread(f)
                        img = ds.pixel_array.astype(float)
                        
                        # Normalize pixel values for display (0-255)
                        img = (np.maximum(img, 0) / img.max()) * 255.0
                        img = np.uint8(img)
                        
                        # Resize for mobile compatibility
                        img = cv2.resize(img, (512, 512))
                        
                        # Convert to 3-channel BGR (CRITICAL for WhatsApp playback)
                        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                        
                        # OPTIONAL: Add Brand Name/Watermark in the corner
                        cv2.putText(img_bgr, 'DR_MOH_SYSTEM', (20, 480), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        
                        slices.append(img_bgr)
                    except Exception as e:
                        st.error(f"Error processing {f.name}")

                if slices:
                    output_path = os.path.join(tmpdir, "patient_scan.mp4")
                    
                    # 4. Video Writer Settings (mp4v is the most stable for Render/Linux)
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
                    # 10 FPS is ideal for medical viewing
                    out = cv2.VideoWriter(output_path, fourcc, 10, (512, 512), True)
                    
                    for s in slices:
                        out.write(s)
                    out.release()
                    
                    # 5. Result and Download
                    st.success("Conversion Complete!")
                    with open(output_path, "rb") as vid:
                        st.download_button(
                            label="📥 DOWNLOAD VIDEO FOR WHATSAPP",
                            data=vid,
                            file_name="Medical_Report.mp4",
                            mime="video/mp4"
                        )
