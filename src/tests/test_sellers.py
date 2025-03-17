import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "A", "last_name": "A", "email": "A@A.ru", "password": "qazwsx"}

    response = await async_client.post("/api/v1/sellers", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    # Check each field individually with appropriate comparison
    assert result_data["id"] is not None
    assert result_data["first_name"] == "A"
    assert result_data["last_name"] == "A"
    assert result_data["email"].lower() == "a@a.ru"  # Case-insensitive comparison


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

    response = await async_client.get("/api/v1/sellers")

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert len(result["sellers"]) == 2

    # Check each seller individually with case-insensitive email comparison
    sellers_data = result["sellers"]
    assert sellers_data[0]["id"] == seller.id
    assert sellers_data[0]["first_name"] == "A"
    assert sellers_data[0]["last_name"] == "A"
    assert sellers_data[0]["email"].lower() == "a@a.ru"

    assert sellers_data[1]["id"] == seller_2.id
    assert sellers_data[1]["first_name"] == "B"
    assert sellers_data[1]["last_name"] == "B"
    assert sellers_data[1]["email"].lower() == "b@b.ru"


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
    await db_session.commit()  # Ensure data is committed

    # Create a test book
    book = books.Book(
        author="Prutkov",
        title="Zri V Koren",
        year=1850,
        pages=10,
        seller_id=seller.id
    )

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()  # Ensure data is committed

    # Get the seller without authentication
    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    result = response.json()
    assert result["id"] == seller.id
    assert result["first_name"] == "A"
    assert result["last_name"] == "A"
    assert result["email"].lower() == "a@a.ru"
    assert len(result["books"]) == 1
    assert result["books"][0]["title"] == "Zri V Koren"


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsx"
    )

    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()  # Ensure data is committed

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(
        first_name="A", last_name="A", email="A@A.ru", hash_password="qazwsx"
    )

    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()  # Ensure data is committed

    update_data = {
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

    result = response.json()
    assert result["id"] == seller.id
    assert result["first_name"] == "vasya"
    assert result["last_name"] == "pupkin"
    assert result["email"].lower() == "vp@vp.ru"


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
    await db_session.commit()  # Ensure data is committed

    # Then try to create another with the same email
    data = {
        "first_name": "B",
        "last_name": "B",
        "email": "duplicate@example.com",  # Same email
        "password": "qazwsx"
    }

    response = await async_client.post("/api/v1/sellers", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "A seller with this email already exists"