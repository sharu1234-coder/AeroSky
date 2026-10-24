from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.food_item import FoodItem


router = APIRouter(prefix="/food", tags=["Food"])


class FoodItemResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    price: Decimal
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=list[FoodItemResponse])
def list_food_items(db: Session = Depends(get_db)):
    return db.scalars(
        select(FoodItem)
        .where(FoodItem.is_available.is_(True))
        .order_by(FoodItem.category, FoodItem.name)
    ).all()
