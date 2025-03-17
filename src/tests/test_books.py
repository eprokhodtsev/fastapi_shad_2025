import pytest
from sqlalchemy import select
from src.models.books import Book
from fastapi import status
from icecream import ic


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(db_session, async_client):
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id
    }
    response = await async_client.post("/api/v1/books", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
        "seller_id": seller.id
    }


@pytest.mark.asyncio
async def test_create_book_with_old_year(db_session, async_client):
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book2@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 1986,
        "seller_id": seller.id
    }
    response = await async_client.post("/api/v1/books", json=data)

    # The API currently accepts any year value
    assert response.status_code == status.HTTP_201_CREATED
    
    result_data = response.json()
    assert result_data["year"] == 1986


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book3@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)
    book_2 = Book(author="Lermontov", title="Mtziri", year=2024, pages=104, seller_id=seller.id)

    db_session.add_all([book, book_2])
    await db_session.flush()
    await db_session.commit()

    response = await async_client.get("/api/v1/books")

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    assert len(result_data["books"]) == 2

    # Проверяем что книги вернулись в правильном порядке
    assert result_data["books"][0]["title"] == "Eugeny Onegin"
    assert result_data["books"][1]["title"] == "Mtziri"


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book4@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    assert result_data == {
        "id": book.id,
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "seller_id": seller.id
    }


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book5@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages=104, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    update_data = {
        "title": "Evgeniy Onegin",
        "author": "Alexander Pushkin",
        "year": 2002,
        "pages": 105,
        "seller_id": seller.id
    }

    response = await async_client.put(f"/api/v1/books/{book.id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK

    result_data = response.json()

    assert result_data == {
        "id": book.id,
        "title": "Evgeniy Onegin",
        "author": "Alexander Pushkin",
        "year": 2002,
        "pages": 105,
        "seller_id": seller.id
    }


@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book6@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    # First create a seller
    from src.models.sellers import Seller
    seller = Seller(
        first_name="Book", last_name="Owner", email="book7@owner.com", hash_password="password"
    )
    db_session.add(seller)
    await db_session.flush()
    await db_session.commit()
    
    book = Book(author="Lermontov", title="Mtziri", pages=510, year=2024, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()
    await db_session.commit()

    response = await async_client.delete("/api/v1/books/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
