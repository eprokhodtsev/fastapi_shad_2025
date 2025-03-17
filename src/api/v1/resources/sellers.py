from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.schemas import SellerCreate, SellerResponse, SellerUpdate, SellerListResponse, SellerDetailResponse
from src.core.db import get_db
from src.crud.sellers import SellerCRUD
from src.crud.books import BookCRUD

router = APIRouter(tags=["Sellers"])


@router.post(
    "/sellers", 
    response_model=SellerResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new seller"
)
async def create_seller(
    seller: SellerCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Check if seller with this email already exists
    existing_seller = await SellerCRUD(db).get_by_email(email=seller.email)
    if existing_seller:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A seller with this email already exists"
        )
    
    return await SellerCRUD(db).create(obj_in=seller)


@router.get(
    "/sellers", 
    response_model=SellerListResponse, 
    summary="Get all sellers"
)
async def get_sellers(
    db: AsyncSession = Depends(get_db)
):
    return {
        "sellers": await SellerCRUD(db).get_multi()
    }


@router.get(
    "/sellers/{seller_id}", 
    response_model=SellerDetailResponse, 
    summary="Get a specific seller with their books"
)
async def get_seller(
    seller_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_seller = await SellerCRUD(db).get(obj_id=seller_id)
    if db_seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seller with id {seller_id} not found"
        )
    
    # Get all books for this seller
    seller_books = await BookCRUD(db).get_by_seller(seller_id=seller_id)
    
    # Build response with seller and their books
    return {
        "id": db_seller.id,
        "first_name": db_seller.first_name,
        "last_name": db_seller.last_name,
        "email": db_seller.email,
        "books": seller_books
    }


@router.put(
    "/sellers/{seller_id}", 
    response_model=SellerResponse, 
    summary="Update a seller"
)
async def update_seller(
    seller_id: int, 
    seller: SellerUpdate, 
    db: AsyncSession = Depends(get_db)
):
    db_seller = await SellerCRUD(db).get(obj_id=seller_id)
    if db_seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seller with id {seller_id} not found"
        )
    
    # Check for email conflicts if email is being updated
    if seller.email and seller.email != db_seller.email:
        existing_seller = await SellerCRUD(db).get_by_email(email=seller.email)
        if existing_seller:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A seller with this email already exists"
            )
    
    return await SellerCRUD(db).update(db_obj=db_seller, obj_in=seller)


@router.delete(
    "/sellers/{seller_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a seller and their books"
)
async def delete_seller(
    seller_id: int, 
    db: AsyncSession = Depends(get_db)
):
    db_seller = await SellerCRUD(db).get(obj_id=seller_id)
    if db_seller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seller with id {seller_id} not found"
        )
    
    # Delete the seller (this should cascade delete their books if set up correctly)
    await SellerCRUD(db).remove(db_obj=db_seller)
    return 