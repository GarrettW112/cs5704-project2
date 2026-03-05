from sqlalchemy.orm import Session
from ScanAndSave.models.inventory import Inventory
from ScanAndSave.schemas.inventory import InventoryCreate

from ScanAndSave.models.item import Item
from ScanAndSave.schemas.item import ItemCreate


# Call this from receipt scanner
def create_inventory_item(db: Session, item_id: int, user_id: int, item: ItemCreate):

    db_inventory = Inventory(
        item_id=item_id,
        user_id=user_id,
        name=item.normalized_name or item.raw_name,
        category=item.category,
        quantity=item.quantity,
        estimated_expiration_date=item.estimated_expiration_date
    )

    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory



def get_user_inventory(db: Session, user_id: int):
    return db.query(Inventory).filter(
        Inventory.user_id == user_id
    ).all()
    

def delete_inventory(db: Session, inventory_id: int, user_id: int):
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.user_id == user_id
    ).first

    if inventory:
        db.delete(inventory)
        db.commit()
    
    return inventory