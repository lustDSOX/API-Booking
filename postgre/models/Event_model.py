from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Float, Integer, String

from postgre.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    event_date = Column(DateTime(timezone=False), nullable=False)
    price = Column(Float, nullable=False)
    total_tickets = Column(Integer, nullable=False)
    available_tickets = Column(Integer, nullable=False)
    update_at = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=True)

    tickets = relationship("Ticket", back_populates="event")