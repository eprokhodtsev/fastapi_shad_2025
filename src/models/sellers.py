from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class Seller(BaseModel):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hash_password = Column(String, nullable=False)
    
    # Add book relationship
    books = relationship("Book", back_populates="seller", cascade="all, delete-orphan")  