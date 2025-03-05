from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from icecream import ic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncommingSeller, ReturnedAllSellers, ReturnedSeller, ReturnedSellerWithBooks, ReturnedAllSellers
from passlib.context import CryptContext  

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Initialize password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: IncommingSeller, session: DBSession):
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        hash_password=pwd_context.hash(seller.password),
    )

    session.add(new_seller)
    await session.flush()

    return new_seller


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller)
    res = await session.execute(query)
    sellers = res.scalars().all()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    res = await session.execute(select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books)))
    seller = res.scalar_one_or_none()
    return seller


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    delete_seller = await session.get(Seller, seller_id)
    ic(delete_seller)
    if delete_seller:
        await session.delete(delete_seller)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    if update_seller := await session.get(Seller, seller_id):
        update_seller.first_name = new_data.first_name
        update_seller.last_name = new_data.last_name
        update_seller.email = new_data.email

        await session.flush()

        return update_seller
    return Response(status_code=status.HTTP_404_NOT_FOUND)
