import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers
from src.routers.v1.token import create_access_token


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "A", "last_name": "A", "email": "A@A.ru", "password": "qazwsx"}

    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": result_data["id"],
        "first_name": "A",
        "last_name": "A",
        "email": "A@A.ru",
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):

    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsx"
    )
    seller_2 = sellers.Seller(first_name="B", last_name="B", email="B@B.ru", hash_password="edcrfv")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2

    assert response.json() == {
        "sellers": [
            {"id": seller.id, "first_name": "A", "last_name": "A", "email": "A@A.ru"},
            {"id": seller_2.id, "first_name": "B", "last_name": "B", "email": "B@B.ru"},
        ]
    }


@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsxedc"
    )
    seller_2 = sellers.Seller(first_name="B", last_name="B", email="B@B.ru", hash_password="edcrfv")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    book = books.Book(author="Prutkov", title="Zri V Koren", year=1850, count_pages=10, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    token = create_access_token({"sub": seller.email})
    response = await async_client.get(f"/api/v1/sellers/{seller.id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "id": seller.id,
        "first_name": "A",
        "last_name": "A",
        "email": "A@A.ru",
        "books": [
            {
                "id": book.id,
                "author": "Prutkov",
                "title": "EZri V Koren",
                "year": 1850,
                "count_pages": 10,
                "seller_id": seller.id,
            }
        ],
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsx"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsx"
    )

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={
            "id": seller.id,
            "first_name": "vasya",
            "last_name": "pupkin",
            "email": "vp@vp.ru",
            "password": "vp",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "vp"
    assert res.last_name == "vp"
    assert res.email == "vp@mvp.ru"