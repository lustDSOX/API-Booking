from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from postgre.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    status = Column(String, nullable=False)
    pdf_path = Column(String, nullable=True)
    update_at = Column(DateTime(timezone=False), nullable=True)
    created_at = Column(DateTime(timezone=False), nullable=False)

    user = relationship("User", back_populates="tickets")
    event = relationship("Event", back_populates="tickets")