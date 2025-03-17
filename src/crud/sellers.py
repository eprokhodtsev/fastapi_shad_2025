from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.sellers import Seller
from src.api.v1.schemas import SellerCreate, SellerUpdate
from src.core.security import get_password_hash

class SellerCRUD:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get(self, obj_id: int) -> Optional[Seller]:
        stmt = select(Seller).where(Seller.id == obj_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[Seller]:
        stmt = select(Seller).where(Seller.email == email)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_multi(self) -> List[Seller]:
        stmt = select(Seller)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: SellerCreate) -> Seller:
        # Hash the password
        hashed_password = get_password_hash(obj_in.password)
        
        # Create the Seller object
        db_obj = Seller(
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            email=obj_in.email,
            hash_password=hashed_password
        )
        
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Seller, obj_in: SellerUpdate) -> Seller:
        # Update the fields if provided
        if obj_in.first_name is not None:
            db_obj.first_name = obj_in.first_name
        if obj_in.last_name is not None:
            db_obj.last_name = obj_in.last_name
        if obj_in.email is not None:
            db_obj.email = obj_in.email
        if obj_in.password is not None:
            db_obj.hash_password = get_password_hash(obj_in.password)
        
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def remove(self, db_obj: Seller) -> Seller:
        await self.db_session.delete(db_obj)
        await self.db_session.commit()
        return db_obj 