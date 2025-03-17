from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

from src.api.v1.schemas.books import BookResponse


class SellerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class SellerCreate(SellerBase):
    password: str


class SellerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class SellerResponse(SellerBase):
    id: int

    class Config:
        from_attributes = True


class SellerListResponse(BaseModel):
    sellers: List[SellerResponse]


class SellerDetailResponse(SellerResponse):
    books: List[BookResponse] = [] 