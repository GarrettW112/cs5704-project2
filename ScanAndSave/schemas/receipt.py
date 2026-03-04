from pydantic import BaseModel
from datetime import date
from decimal import Decimal

class ReceiptBase(BaseModel):
    store: str
    purchase_date: date
    total_amount: Decimal

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptResponse(ReceiptBase):
    receipt_id: int
    user_id: int

    class Config:
        from_attributes = True