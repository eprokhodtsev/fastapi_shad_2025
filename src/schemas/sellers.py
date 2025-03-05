from pydantic import BaseModel

from .books import ReturnedBook

__all__ = ["IncommingSeller", "ReturnedSeller", "ReturnedAllSellers", "ReturnedSellerWithBooks"]


class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    email: str


class IncommingSeller(BaseSeller):
    password: str


class ReturnedSeller(BaseSeller):
    id: int


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]


class ReturnedSellerWithBooks(BaseSeller):
    id: int
    books: list[ReturnedBook]