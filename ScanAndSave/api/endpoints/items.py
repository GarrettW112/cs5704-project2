from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ScanAndSave.schemas.item import ItemResponse, ItemCreate, ItemUpdate
from ScanAndSave.crud import crud_item
from ScanAndSave.api.endpoints.deps import get_database, get_current_user
from ScanAndSave.models.user import User


router = APIRouter()

# get all items by user id
@router.get("/", response_model=list[ItemResponse])
def read_items(db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):
    
    items = crud_item.get_user_items(
        db=db,
        user_id=current_user.id
    )
    
    return items

@router.get("/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):

    item = crud_item.get_item(
        db=db,
        item_id=item_id,
        user_id=current_user.id
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item

@router.post("/", response_model=ItemResponse)
def create_new_item(item_in: ItemCreate, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):
    db_item = crud_item.create_item(
        db=db,
        item=item_in,
    )

    return db_item

@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, update: ItemUpdate, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):
    
    db_item = crud_item.update_item(
        db=db,
        item_id=item_id,
        user_id=current_user.id,
        new_data=update.dict(exclude_unset=True)
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return db_item

@router.delete("/{item_id}", response_model=ItemResponse)
def delete_item(item_id: int, db: Session = Depends(get_database), current_user: User = Depends(get_current_user)):
    
    item = crud_item.delete_item(
        db=db,
        item_id=item_id,
        user_id=current_user.id
    )

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item