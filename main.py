import shutil
import tempfile
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from pipeline.receipt_pipeline import ReceiptPipeline # Adjust path

app = FastAPI()
pipeline = ReceiptPipeline()

@app.post("/process-receipt/")
async def process_receipt(file: UploadFile = File(...)):
    # Create the temp file, but don't use the 'with' block context for the run
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
    try:
        shutil.copyfileobj(file.file, temp)
        temp.close()  # <--- CLOSE IT HERE so the Agent can open it
        
        # Now the Agent has permission to read it
        result = pipeline.run(temp.name)
    finally:
        # Manually delete it since we used delete=False
        if os.path.exists(temp.name):
            os.remove(temp.name)
            
    return result