import datetime
import enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from postgre.database import Base
from postgre.managers.Event_manager import EventManager
from postgre.models.Ticket_model import Ticket

class TicketStatus(str,enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class TicketManager(Base):
    def __init__(self, session:AsyncSession):
        self.session = session

    async def create(self, user_id:int, event_id:int, count: int):
        tickets = [
            Ticket(user_id=user_id, event_id=event_id)
            for _ in range(count)
        ]

        try:
            self.session.add_all(tickets)
            await self.session.flush()
            return tickets
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def get_by_user_id(self, user_id:int) -> list[Ticket]:
        stmt = (
            select(Ticket).
            where(Ticket.user_id == user_id)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalars().all()
        except Exception as e:
            raise e

    async def get_by_event_id(self, event_id:int) -> list[Ticket]:
        stmt = (
            select(Ticket).
            where(Ticket.event_id == event_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def change_status(self, tickets_id: list[int], status: TicketStatus):
        try: 
            for id in tickets_id:
                ticket = await self.get_by_id(id)
                ticket.status = status
                if ticket.status == TicketStatus.PAID:
                    ticket.pdf_path = f"pdf/{id}_{ticket.event_id}.pdf"
            await self.session.flush()
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def get_by_id(self, id:int) -> Ticket:
        stmt = (
            select(Ticket).
            where(Ticket.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    

