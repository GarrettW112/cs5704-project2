from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from ScanAndSave.api.endpoints.deps import get_database
from ScanAndSave.schemas.receipt import ReceiptCreate, ReceiptResponse
from ScanAndSave.crud import crud_receipt
from ScanAndSave.models.receipt import Receipt
from ScanAndSave.pipeline.receipt_pipeline import ReceiptPipeline # Adjust path
router = APIRouter()
pipeline = ReceiptPipeline()

@router.post("/process-receipt/")
async def process_receipt(file: UploadFile = File(...), db: Session = Depends(get_database)):

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
            
    # parse result and store receipt in db
    return result

@router.post("/add-receipt/")
async def add_receipt(receipt: ReceiptCreate, db: Session = Depends(get_database)):

    # TEMP: hardcode a user ID for testing
    user_id = 1

    # Use your CRUD layer to save the receipt
    db_receipt = crud_receipt.create_receipt(
        db=db,
        receipt=receipt,
        user_id=user_id
    )

    return db_receipt