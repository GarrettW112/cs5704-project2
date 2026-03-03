from sqlalchemy import Column, DateTime, Integer, String # Whatever imports are needed
from ScanAndSave.database.session import Base

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    store = Column(String(100), unique=True)
    