import streamlit as st
import pydicom
import numpy as np
import imageio
import tempfile
import os

st.set_page_config(page_title="WhatsApp DICOM", layout="centered")

# Professional UI
st.markdown("<style>.stButton>button {background-color: #25D366; color: white; border-radius: 10px; width: 100%; font-weight: bold;}</style>", unsafe_allow_html=True)

st.title("Medical DICOM to WhatsApp ⚕️")

uploaded_files = st.file_uploader("Upload DICOM Files", accept_multiple_files=True)

if uploaded_files:
    if st.button("GENERATE FOR WHATSAPP"):
        with st.spinner("Optimizing for WhatsApp..."):
            slices = []
            # Sort files
            files = sorted(uploaded_files, key=lambda x: x.name)
            
            for f in files:
                try:
                    ds = pydicom.dcmread(f)
                    img = ds.pixel_array.astype(float)
                    # Fast Normalization
                    img = ((img - np.min(img)) / (np.max(img) - np.min(img)) * 255).astype(np.uint8)
                    slices.append(img)
                except:
                    continue

            if slices:
                # Create a temporary file
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, "whatsapp_video.mp4")
                
                # Using imageio with ffmpeg for H.264 encoding (The secret to WhatsApp compatibility)
                # fps=15, quality=7, pixel_format='yuv420p' (Essential for mobile)
                imageio.mimwrite(output_path, slices, fps=15, macro_block_size=16, 
                                 ffmpeg_params=["-vcodec", "libx264", "-pix_fmt", "yuv420p"])

                with open(output_path, "rb") as vid:
                    data = vid.read()
                    st.success("Ready for WhatsApp! ✅")
                    st.download_button(
                        label="📥 DOWNLOAD & SHARE TO WHATSAPP",
                        data=data,
                        file_name="Medical_Scan.mp4",
                        mime="video/mp4"
                    )
