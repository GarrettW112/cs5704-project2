from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ScanAndSave.api.endpoints.deps import get_database, get_current_user
from ScanAndSave.schemas.inventory import InventoryResponse
from ScanAndSave.models.user import User
from ScanAndSave.crud import crud_inventory

router = APIRouter()

# get all inventory by user id
@router.get("/", response_model=list[InventoryResponse])
def read_inventory(db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):

    inventory = crud_inventory.get_user_inventory(
        db=db,
        user_id=current_user.id
    )
    return inventory

# Delete item in inventory
@router.delete("/{inventory_id}", response_model=InventoryResponse)
def delete_inventory(inventory_id: int, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):
    
    inventory = crud_inventory.delete_inventory(
        db=db,
        inventory_id=inventory_id,
        user_id=current_user.id
    )

    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory Item not found")

    return True