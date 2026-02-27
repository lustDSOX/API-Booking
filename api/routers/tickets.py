from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_current_user
from postgre.database import get_db
from postgre.managers.Ticket_manager import TicketManager, TicketStatus
from postgre.models.User_model import User

router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
    dependencies=[Depends(get_current_user)]
)
        
@router.get("/{ticket_id}")
async def get_ticket(ticket_id: int, session:AsyncSession = Depends(get_db)):
    manager = TicketManager(session)
    try:
        ticket = await manager.get_by_id(ticket_id)
        return ticket
    except Exception as e:
        raise e
        
@router.get("/user")
async def get_by_user(session:AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return user.tickets
    

@router.get("/event")
async def get_by_event(event_id: int, session:AsyncSession = Depends(get_db)):
    manager = TicketManager(session)
    try:
        tickets = await manager.get_by_event_id(event_id)
        return tickets
    except Exception as e:
        raise e
        
@router.put("/update")
async def update_ticket(tickets_id: list[int], status: TicketStatus, session:AsyncSession = Depends(get_db)):
    manager = TicketManager(session)
    try:
        await manager.change_status(tickets_id, status)
        return {"message": "Tickets updated successfully"}
    except Exception as e:
        raise e
        
