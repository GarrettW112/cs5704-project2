from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from ScanAndSave.api.endpoints.deps import get_database, get_current_user
from ScanAndSave.schemas.receipt import ReceiptCreate, ReceiptUpdate, ReceiptResponse
from ScanAndSave.crud import crud_receipt
from ScanAndSave.models.receipt import Receipt
from ScanAndSave.models.user import User
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