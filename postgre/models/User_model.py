from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Integer, String

from postgre.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, default="user", nullable=False)
    telegram_id = Column(Integer, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=True)
    refresh_token = Column(String, nullable=True)
    tickets = Column(Integer, default=0)
    expires_at = Column(DateTime(timezone=False), nullable=True)

    tickets = relationship("Ticket", back_populates="user")