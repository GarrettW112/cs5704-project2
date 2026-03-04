from sqlalchemy import Column, DateTime, Integer, String # Whatever imports are needed
from ScanAndSave.database.session import Base

class Receipt(Base):
    __tablename__ = "receipts"

    receipt_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    store = Column(String(100), unique=True)
    # purchase_date DATE,
    # subtotal DECIMAL(10,2),
    # tax DECIMAL(10,2),
    # total DECIMAL(10,2),
    # created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    # FOREIGN KEY (user_id) 
    #     REFERENCES users(id) 
    #     ON DELETE CASCADE