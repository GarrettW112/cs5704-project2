from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from ScanAndSave.api.endpoints.deps import get_database, get_current_user
from ScanAndSave.schemas.receipt import ReceiptCreate, ReceiptUpdate, ReceiptResponse
from ScanAndSave.crud import crud_receipt
from ScanAndSave.models.receipt import Receipt
from ScanAndSave.models.user import User
from ScanAndSave.pipeline.receipt_pipeline import ReceiptPipeline # Adjust path
import tempfile
import shutil
import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path

router = APIRouter()
pipeline = ReceiptPipeline()

@router.post("/process-receipt/", response_model=ReceiptResponse)
async def process_receipt(
    file: UploadFile = File(...), 
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_user)
):

    # Create temp file path
    suffix = Path(file.filename).suffix
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            shutil.copyfileobj(file.file, temp)
            temp_path = temp.name

        # IMPORTANT: close the uploaded file
        await file.close()

        # Run pipeline AFTER file handles are closed
        result = pipeline.run(temp_path)

    finally:
        # Delete file safely
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except PermissionError:
                print("Warning: temp file still locked, skipping delete")

    if not result:
        raise HTTPException(status_code=400, detail="Failed to process receipt")

    # ---- Parse AI output ----
    try:
        store = result.get("merchant", "Unknown Store")
        total = Decimal(str(result.get("total", 0)))

        # Convert date string "09/21/20" → datetime.date
        raw_date = result.get("date")
        purchase_date = datetime.strptime(raw_date, "%m/%d/%y").date()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing AI output: {str(e)}")

    # ---- Create Receipt Schema ----
    receipt_data = ReceiptCreate(
        store=store,
        purchase_date=purchase_date,
        total_amount=total
    )

    # ---- Save to DB ----
    db_receipt = crud_receipt.create_receipt(
        db=db,
        receipt=receipt_data,
        user_id=current_user.id
    )

    return db_receipt

@router.post("/add-receipt/")
async def add_receipt(receipt: ReceiptCreate, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):

    # Use your CRUD layer to save the receipt
    db_receipt = crud_receipt.create_receipt(
        db=db,
        receipt=receipt,
        user_id=current_user.id
    )

    return db_receipt

# Get all receipts by user ID
@router.get("/", response_model=list[ReceiptResponse])
def get_receipts(db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):

    receipts = crud_receipt.get_user_receipts(
        db=db, 
        user_id=current_user.id)

    return receipts

# Get a receipt by receipt ID
@router.get("/{receipt_id}", response_model=ReceiptResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):

    receipt = crud_receipt.get_receipt(
        db=db, 
        receipt_id=receipt_id)
    
    if not receipt or receipt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt

# Update receipt
@router.put("/{receipt_id}", response_model=ReceiptResponse)
def update_receipt(receipt_id: int, update: ReceiptUpdate, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):
    
    db_receipt = crud_receipt.update_receipt(
        db=db,
        receipt_id=receipt_id,
        user_id=current_user.id,
        new_data=update.dict(exclude_unset=True)
    )
    if not db_receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return db_receipt


# Delete receipt
@router.delete("/{receipt_id}", response_model=ReceiptResponse)
def delete_receipt(receipt_id: int, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):

    receipt = crud_receipt.delete_receipt(
        db=db, 
        receipt_id=receipt_id, 
        user_id=current_user.id)
    
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt