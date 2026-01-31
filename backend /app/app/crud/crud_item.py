from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD operations for Item model with owner support."""

    def create_with_owner(
        self, db: Session, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        """
        Create a new Item and assign it to an owner.

        Args:
            db (Session): SQLAlchemy session
            obj_in (ItemCreate): Pydantic schema for Item creation
            owner_id (int): ID of the owner

        Returns:
            Item: Created Item instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        """
        Retrieve multiple Items for a specific owner.

        Args:
            db (Session): SQLAlchemy session
            owner_id (int): Owner's user ID
            skip (int): Number of items to skip (pagination)
            limit (int): Maximum number of items to return

        Returns:
            List[Item]: List of Item instances
        """
        return (
            db.query(self.model)
            .filter(self.model.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


item = CRUDItem(Item)
