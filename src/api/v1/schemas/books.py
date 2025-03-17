from typing import List, Optional
from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: str
    year: int
    pages: int
    seller_id: int  # Add seller_id field


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    pages: Optional[int] = None
    seller_id: Optional[int] = None  # Add optional seller_id for updates


class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    books: List[BookResponse] 