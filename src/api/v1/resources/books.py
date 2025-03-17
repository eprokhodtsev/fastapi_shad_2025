from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import BookCreate, BookUpdate, BookResponse, BookListResponse
from src.core.db import get_db
from src.crud.books import BookCRUD
from src.crud.sellers import SellerCRUD

router = APIRouter(tags=["Books"])


@router.post(
    "/books", 
    response_model=BookResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book"
)
async def create_book(
    book: BookCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Check if the seller exists
    if book.seller_id:
        seller = await SellerCRUD(db).get(book.seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Seller with id {book.seller_id} not found"
            )
    
    return await BookCRUD(db).create(obj_in=book)


@router.get(
    "/books", 
    response_model=BookListResponse, 
    summary="Get all books"
)
async def get_books(
    db: AsyncSession = Depends(get_db)
):
    return {
        "books": await BookCRUD(db).get_multi()
    }


@router.put(
    "/books/{book_id}", 
    response_model=BookResponse, 
    summary="Update a book"
)
async def update_book(
    book_id: int, 
    book: BookUpdate, 
    db: AsyncSession = Depends(get_db)
):
    db_book = await BookCRUD(db).get(obj_id=book_id)
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    
    # Check if the seller exists when updating seller_id
    if book.seller_id:
        seller = await SellerCRUD(db).get(book.seller_id)
        if not seller:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Seller with id {book.seller_id} not found"
            )
    
    return await BookCRUD(db).update(db_obj=db_book, obj_in=book)


@router.get(
    "/books/{book_id}", 
    response_model=BookResponse, 
    summary="Get a specific book"
)
async def get_book(
    book_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_book = await BookCRUD(db).get(obj_id=book_id)
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return db_book


@router.delete(
    "/books/{book_id}", 
    response_model=BookResponse, 
    summary="Delete a book"
)
async def delete_book(
    book_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_book = await BookCRUD(db).get(obj_id=book_id)
    if db_book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )
    return await BookCRUD(db).remove(db_obj=db_book) 