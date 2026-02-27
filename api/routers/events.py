import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from api.dependencies import get_admin_user, get_current_user
from postgre.database import get_db
from postgre.managers.Event_manager import EventManager
from postgre.managers.Ticket_manager import TicketManager
from sqlalchemy.ext.asyncio import AsyncSession

from postgre.models.User_model import User

public_router = APIRouter(
    prefix="/public/events",
    tags=["Events"]
)

user_router = APIRouter(
    prefix="/events",
    tags=["Events"],
    dependencies=[Depends(get_current_user)]
)

admin_router = APIRouter(
    prefix="/admin/events",
    tags=["Events"],
    dependencies=[Depends(get_admin_user)]
)

class EventCreate(BaseModel):
    title: str = Field(..., example="Концерт Rammstein")
    description: str
    event_date: datetime = Field(..., example="2026-05-20T19:00:00")
    price: float = Field(..., gt=0, example=2500.50)
    total_tickets: int = Field(..., gt=0, example=5000)

@public_router.get("/")
async def get_events(offset: int = 0, limit: int = 10, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    events = await manager.get_all_list(offset, limit)
    return events
    
@public_router.get("/search")
async def search_events(title: str, offset: int = 0, limit: int = 10, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    events = await manager.get_by_title(title, offset, limit)
    return events
    
@public_router.get("/date")
async def search_by_date(date_start: datetime, date_end: datetime, offset: int = 0, limit: int = 10, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    events = await manager.get_by_date(date_start, date_end, offset, limit)
    return events
    
@public_router.get("/price")
async def search_by_price(price_min: float, price_max: float, offset: int = 0, limit: int = 10, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    events = await manager.get_by_price(price_min, price_max, offset, limit)
    return events

@admin_router.put("/{event_id}")
async def update_event(event_id: int, event: EventCreate, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    _event = await manager.get_by_id(event_id)
    if not _event:
        raise ValueError("Event not found")
    try:
        _event.title = event.title
        _event.description = event.description
        _event.event_date = event.event_date
        _event.price = event.price
        _event.total_tickets = event.total_tickets
        await session.commit()      
        await session.refresh(_event)
    except Exception as e:
        raise e

@admin_router.delete("/{event_id}")
async def delete_event(event_id: int, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    try:
        event = await manager.get_by_id(event_id)
        if not event:
            raise ValueError("Event not found")
        await manager.delete(event)
        await session.commit()
        return {"message": "Event deleted successfully"}
    except Exception as e:
        raise e
        
@user_router.post("/reserve")
async def reserve_tickets(event_id: int, tickets_count: int, session:AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    event_manager = EventManager(session)
    ticket_manager = TicketManager(session)
    try:
        reserve = await event_manager.reserve_tickets(event_id, tickets_count)
        if reserve:
            await ticket_manager.create(user.id, event_id, tickets_count)
            await session.commit()
            return {"message": "Tickets reserved successfully"}
        else:
            raise ValueError("Not enough tickets available")
    except Exception as e:
        raise e

@public_router.get("/{event_id}")
async def get_event(event_id: int, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    event = await manager.get_by_id(event_id)
    return event
    
@admin_router.get("/stats")
async def get_stats(event_id:int, session:AsyncSession = Depends(get_db)):
    manager = EventManager(session)
    stats = await manager.get_stats(event_id)
    return stats

@admin_router.post("/create")
async def create_event(event: EventCreate, session:AsyncSession = Depends(get_db), admin: User = Depends(get_admin_user)):
    manager = EventManager(session)
    event = await manager.create(
        event.title,
        event.description,
        event.event_date,
        event.price,
        event.total_tickets
    )
    await session.commit()
    return event