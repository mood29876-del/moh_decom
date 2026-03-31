import os
import cv2
import numpy as np
import pydicom
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

app = FastAPI()

# Pure English UI Design
HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DICOM to MP4 Converter</title>
    <style>
        :root { --primary: #2563eb; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { background: var(--card); padding: 2.5rem; border-radius: 1rem; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); width: 100%; max-width: 400px; text-align: center; border: 1px solid #334155; }
        h1 { font-size: 1.5rem; margin-bottom: 0.5rem; color: #60a5fa; }
        p { color: #94a3b8; font-size: 0.9rem; margin-bottom: 2rem; }
        .drop-zone { border: 2px dashed #475569; padding: 2rem; border-radius: 0.75rem; margin-bottom: 1.5rem; transition: 0.3s; }
        .drop-zone:hover { border-color: var(--primary); background: #1e293b; }
        input[type="file"] { margin-bottom: 1rem; width: 100%; cursor: pointer; color: #94a3b8; }
        button { background: var(--primary); color: white; border: none; padding: 1rem; border-radius: 0.5rem; font-weight: bold; width: 100%; cursor: pointer; transition: 0.2s; font-size: 1rem; }
        button:hover { background: #1d4ed8; transform: translateY(-1px); }
        .info { margin-top: 1.5rem; font-size: 0.7rem; color: #64748b; }
    </style>
</head>
<body>
    <div class="container">
        <h1>DICOM Converter</h1>
        <p>Medical Imaging Video Processor</p>
        <form action="/convert/" method="post" enctype="multipart/form-data">
            <div class="drop-zone">
                <input type="file" name="files" multiple required accept=".dcm">
            </div>
            <button type="submit">Process & Download</button>
        </form>
        <div class="info">Supported: .dcm files only</div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_INTERFACE

@app.post("/convert/")
async def convert_process(files: list[UploadFile] = File(...)):
    temp_dir = "processing_vault"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # Save and Sort
    valid_paths = []
    for f in files:
        path = os.path.join(temp_dir, f.filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        valid_paths.append(path)
    
    valid_paths.sort()

    # Frame Extraction
    frames = []
    for p in valid_paths:
        try:
            ds = pydicom.dcmread(p)
            pixel_data = ds.pixel_array.astype(float)
            pixel_data = (np.maximum(pixel_data, 0) / pixel_data.max()) * 255.0
            frames.append(np.uint8(pixel_data))
        except:
            continue

    if not frames:
        raise HTTPException(status_code=400, detail="Processing failed: No valid frames found.")

    # Video Assembly
    output_file = "medical_scan_result.mp4"
    h, w = frames[0].shape
    writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), 10, (w, h), False)
    
    for frame in frames:
        writer.write(frame)
    writer.release()

    return FileResponse(output_file, media_type='video/mp4', filename="scan_output.mp4")