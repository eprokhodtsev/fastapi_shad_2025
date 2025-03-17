from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.books import Book
from src.api.v1.schemas import BookCreate, BookUpdate


class BookCRUD:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get(self, obj_id: int) -> Optional[Book]:
        stmt = select(Book).where(Book.id == obj_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_multi(self) -> List[Book]:
        stmt = select(Book)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()
        
    async def get_by_seller(self, seller_id: int) -> List[Book]:
        """Get all books for a specific seller."""
        stmt = select(Book).where(Book.seller_id == seller_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: BookCreate) -> Book:
        db_obj = Book(
            title=obj_in.title,
            author=obj_in.author,
            year=obj_in.year,
            pages=obj_in.pages,
            seller_id=obj_in.seller_id
        )
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Book, obj_in: BookUpdate) -> Book:
        update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.db_session.add(db_obj)
        await self.db_session.commit()
        await self.db_session.refresh(db_obj)
        return db_obj

    async def remove(self, db_obj: Book) -> Book:
        await self.db_session.delete(db_obj)
        await self.db_session.commit()
        return db_obj 