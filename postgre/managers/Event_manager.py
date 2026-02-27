import datetime
from postgre.managers.Ticket_manager import TicketStatus
from postgre.models.Event_model import Event
from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from postgre.models.Ticket_model import Ticket


class EventManager:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def create(self, title:str, description:str, event_date:datetime, price:float, total_tickets:int) -> Event:
        event = Event(
            title=title,
            description=description,
            event_date=event_date,
            price=price,
            total_tickets=total_tickets
        )
        self.session.add(event)
        try:
            await self.session.flush()
            await self.session.refresh(event)
            return event
        except Exception as e:
            await self.session.rollback()
            raise e


    async def get_all_list(self, offset: int, limit: int) -> list[Event]:
        stmt = (
            select(Event)
            .order_by(Event.event_date.desc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_title(self, title: str, offset: int, limit: int) -> list[Event]:
        stmt = (
            select(Event).
            where(Event.title.ilike(f"%{title}%"))
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_date(self, date_start: datetime, date_end: datetime, offset: int, limit: int) -> list[Event]:
        stmt = (
            select(Event)
            .where(Event.event_date.between(date_start,date_end))
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def get_by_price(self, price_min: float, price_max: float, offset: int, limit: int) -> list[Event]:
        stmt = (
            select(Event)
            .where(Event.price.between(price_min,price_max))
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
        
    async def get_by_id(self, id:int) -> Event:
        stmt = (
            select(Event).
            where(Event.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def delete(self, event:Event):
        try:
            await self.session.delete(event)
            
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def get_stats(self, event_id:int):
        stmt = (
            select(
                Event.id,
                Event.total_tickets,
                Event.available_tickets,
                func.count(Ticket.id).label("sold_tickets"),
                (func.count(Ticket.id) * Event.price).label("revenue")
            )
            .outerjoin(
                Ticket,
                and_(
                    Ticket.event_id == Event.id,
                    Ticket.status == TicketStatus.PAID
                )
            )
            .where(Event.id == event_id)
            .group_by(Event.id)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if row is None:
            return None
        return row

    async def reserve_tickets(self, event_id:int, tickets_count:int) -> bool:
        stmt = (
            update(Event)
            .where(
                and_(
                    Event.id == event_id,
                    Event.available_tickets >= tickets_count
                )
            )
            .values(available_tickets=Event.available_tickets - tickets_count)
            .returning(Event.id)            
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            await self.session.rollback()
            raise e
    
    async def return_tickets(self, event_id:int, tickets_count:int) -> bool:
        stmt = (
            update(Event)
            .where(Event.id == event_id)
            .values(available_tickets=Event.available_tickets + tickets_count)
            .returning(Event.id)            
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    