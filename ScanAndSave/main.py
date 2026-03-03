import shutil
import tempfile
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from ScanAndSave.pipeline.receipt_pipeline import ReceiptPipeline # Adjust path
from ScanAndSave.database.session import engine, Base
from ScanAndSave.models import user # Import all models to register them

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


from ScanAndSave.api.endpoints import users, auth

app.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"]
)

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only; narrow this down for your VT project later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)