from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.external.dict_codes import get_email_code, set_email_code
from api.external.email_code import send_code
from api.security import create_access_token, create_refresh_token, hash_refresh_token
from postgre.database import get_db
from postgre.managers.User_manager import UserManager


router = APIRouter(
    prefix="/login",
    tags=["login"]
)


@router.post("/telegram")
async def login_telegram(telegram_id: int, session: AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    user = await manager.get_by_telegram_id(telegram_id)

    if not user:
        await manager.create(telegram_id, None)
        await session.commit()
    
    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    refresh = await manager.set_refresh(user)
    await session.commit()
    await session.refresh(user)

    return {"access_token": token, "refresh_token": refresh}

@router.post("/email/verify_code")
async def verify_code(email: str, code: str, session: AsyncSession = Depends(get_db)):
    ver_code = get_email_code(email)
    if ver_code != code:
        raise HTTPException(status_code=401, detail="Invalid code")

    manager = UserManager(session)
    user = await manager.get_by_email(email)

    if not user:
        await manager.create(None, email)
        await session.commit()
    
    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    refresh = await manager.set_refresh(user)
    await session.commit()
    await session.refresh(user)

    return {"access_token": token, "refresh_token": refresh}


@router.post("/email/send_code")
async def send_email_code(email: str, session: AsyncSession = Depends(get_db)):
    code = await send_code(email)
    await set_email_code(email, code)
    return {"message": "Code sent successfully"}

@router.post("/refresh")
async def refresh_token(refresh: str, session: AsyncSession = Depends(get_db)):
    manager = UserManager(session)
    try:
        hash = hash_refresh_token(refresh)
        user = await manager.get_by_refresh(hash)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        if user.expires_at-datetime.utcnow() > timedelta(days=1):
            refresh = await manager.set_refresh(user)

        token = create_access_token(data={"sub": str(user.id), "role": user.role})
        
        return {"access_token": token, "refresh_token": refresh}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))