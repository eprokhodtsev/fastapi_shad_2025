import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


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
    # Create test sellers
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsx"
    )
    seller_2 = sellers.Seller(
        first_name="B", last_name="B", email="B@B.ru", hash_password="edcrfv"
    )

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
    # Create test sellers
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsxedc"
    )
    seller_2 = sellers.Seller(
        first_name="B", last_name="B", email="B@B.ru", hash_password="edcrfv"
    )

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    # Create a test book
    book = books.Book(
        author="Prutkov", 
        title="Zri V Koren", 
        year=1850, 
        count_pages=10, 
        seller_id=seller.id
    )

    db_session.add(book)
    await db_session.flush()

    # Get the seller without authentication
    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

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
                "title": "Zri V Koren",
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

    update_data = {
        "id": seller.id,
        "first_name": "vasya",
        "last_name": "pupkin",
        "email": "vp@vp.ru",
        "password": "vp",
    }

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json=update_data,
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == "vasya"
    assert res.last_name == "pupkin"
    assert res.email == "vp@vp.ru"


# Additional tests for error cases

@pytest.mark.asyncio
async def test_get_nonexistent_seller(async_client):
    """Test getting a seller that doesn't exist returns 404."""
    response = await async_client.get("/api/v1/sellers/999999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_seller_duplicate_email(db_session, async_client):
    """Test creating a seller with duplicate email returns 400."""
    # First create a seller
    seller = sellers.Seller(
        first_name="A", last_name="A", email="duplicate@example.com", hash_password="qazwsx"
    )
    db_session.add(seller)
    await db_session.flush()
    
    # Then try to create another with the same email
    data = {
        "first_name": "B", 
        "last_name": "B", 
        "email": "duplicate@example.com",  # Same email
        "password": "qazwsx"
    }
    
    response = await async_client.post("/api/v1/sellers/", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST