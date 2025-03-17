from sqlalchemy.ext.asyncio import AsyncSession
from src.models.sellers import Seller
from src.models.books import Book
from src.core.security import get_password_hash

async def init_test_data(db: AsyncSession):
    """
    Инициализирует базу данных тестовыми данными
    """
    # Проверяем, есть ли уже данные в таблице продавцов
    result = await db.execute("SELECT COUNT(*) FROM sellers")
    count = result.scalar()
    
    if count > 0:
        print("База данных уже содержит тестовые данные. Пропускаем инициализацию.")
        return
    
    print("Добавляем тестовые данные в базу данных...")
    
    # Создаем тестовых продавцов
    sellers_data = [
        {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivan@example.com",
            "password": "password123"
        },
        {
            "first_name": "Анна",
            "last_name": "Петрова",
            "email": "anna@example.com",
            "password": "secure456"
        },
        {
            "first_name": "Сергей",
            "last_name": "Сидоров",
            "email": "sergey@example.com",
            "password": "qwerty789"
        }
    ]
    
    sellers = []
    for seller_data in sellers_data:
        seller = Seller(
            first_name=seller_data["first_name"],
            last_name=seller_data["last_name"],
            email=seller_data["email"],
            hash_password=get_password_hash(seller_data["password"])
        )
        db.add(seller)
        sellers.append(seller)
    
    # Сохраняем продавцов, чтобы получить их ID
    await db.flush()
    
    # Создаем тестовые книги
    books_data = [
        {
            "title": "Война и мир",
            "author": "Лев Толстой",
            "year": 2020,
            "pages": 1225,
            "seller_index": 0
        },
        {
            "title": "Преступление и наказание",
            "author": "Федор Достоевский",
            "year": 2019,
            "pages": 592,
            "seller_index": 0
        },
        {
            "title": "Мастер и Маргарита",
            "author": "Михаил Булгаков",
            "year": 2021,
            "pages": 448,
            "seller_index": 1
        },
        {
            "title": "Гарри Поттер и философский камень",
            "author": "Дж. К. Роулинг",
            "year": 2022,
            "pages": 352,
            "seller_index": 1
        },
        {
            "title": "1984",
            "author": "Джордж Оруэлл",
            "year": 2018,
            "pages": 328,
            "seller_index": 2
        },
        {
            "title": "Евгений Онегин",
            "author": "Александр Пушкин",
            "year": 2023,
            "pages": 224,
            "seller_index": 2
        }
    ]
    
    for book_data in books_data:
        seller_index = book_data.pop("seller_index")
        book = Book(
            **book_data,
            seller_id=sellers[seller_index].id
        )
        db.add(book)
    
    # Сохраняем все изменения
    await db.commit()
    
    print("Тестовые данные успешно добавлены!")
    print(f"Создано {len(sellers)} продавцов и {len(books_data)} книг.") 