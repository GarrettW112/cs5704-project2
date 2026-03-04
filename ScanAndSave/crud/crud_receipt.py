from sqlalchemy.orm import Session
from ScanAndSave.models.receipt import Receipt
from ScanAndSave.schemas.receipt import ReceiptCreate

def create_receipt(db: Session, receipt: ReceiptCreate, user_id: int):
    # Create the model instance
    db_receipt = Receipt(
        user_id=user_id,
        store=receipt.store,
        purchase_date=receipt.purchase_date,
        total_amount=receipt.total_amount
    )
    
    # Save to MySQL
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt