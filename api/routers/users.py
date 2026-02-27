from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_admin_user
from postgre.database import get_db
from postgre.managers.User_manager import UserManager


router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_admin_user)]
)

@router.get("/telegram_id")
async def get_user_by_telegram_id(telegram_id: int, session:AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    return await manager.get_by_telegram_id(telegram_id)
    
@router.get("/email")
async def get_user_by_email(email: str, session:AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    return await manager.get_by_email(email)
        
    
@router.get("/")
async def get_users(id:int, session:AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    return await manager.get_by_id(id)

@router.post("/")
async def create_user(telegram_id: int| None, email: str|None, role: str = "user", session:AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    user = await manager.create(telegram_id, email, role)
    await session.commit()
    return user

@router.put("/")
async def update_user(id: int ,telegram_id: int| None = None, email: str|None = None, role: str|None = None, session:AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    if await manager.exist(telegram_id, email):
        user = await manager.get_by_id(id)
        if email is not None:
            user.email = email
        if role is not None:
            user.role = role
        if telegram_id is not None:
            user.telegram_id = telegram_id
        await session.commit()
        await session.refresh(user)
        return user
    else:
        raise ValueError("User does not exist")