from datetime import datetime, timedelta

from sqlalchemy import exists, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api.security import create_refresh_token, hash_refresh_token
from postgre.models.User_model import User

class UserManager:
    def __init__(self, session:AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id:int) -> User:
        stmt = (
            select(User)
            .options(selectinload(User.tickets))
            .where(User.telegram_id == telegram_id)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise e

    async def get_by_email(self, email:str) -> User:
        stmt = (
            select(User)
            .options(selectinload(User.tickets))
            .where(User.email == email)
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise e

    async def exist(self, telegram_id:int|None, email:str|None) -> bool:
        stmt = (
            select(
                exists().
                   where(
                       or_(
                            User.telegram_id == telegram_id if telegram_id else False,
                            User.email == email if email else False
                       )
                    )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar()


    async def create(self, telegram_id:int|None, email:str|None, role:str|None = None) -> User:
        if await self.exist(telegram_id, email):
            raise ValueError("User already exists")
        
        user_data = {
            "telegram_id": telegram_id,
            "email": email,
        }

        if role is not None:
            user_data["role"] = role

        user = User(**user_data)
        self.session.add(user)
        try:
            await self.session.flush()
            await self.session.refresh(user)
            return user
        except Exception as e:
            await self.session.rollback()
            raise e
        
    async def set_refresh(self, user:User) -> str:
        try:
            refresh = create_refresh_token()
            user.refresh_token = hash_refresh_token(refresh)
            return refresh
        except Exception as e:
            raise e

    async def get_by_refresh(self, hash:str) -> User:
        stmt = (
            select(User)
            .where(User.refresh_token == hash)
        )

        try:
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise e
        
    async def get_by_id(self, id:int) -> User:
        stmt = (
            select(User)
            .where(User.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        