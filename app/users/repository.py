from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import raiseload

from app.users.interfaces.repository import IUserRepository
from app.users.models import User


class UserRepository(IUserRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_email(self, email: str) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(User).options(raiseload("*")).where(User.email == email)
            )
            return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(User).options(raiseload("*")).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: str,
    ) -> User:
        async with self._session_factory() as session:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                hashed_password=hashed_password,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def update_password(self, user_id: UUID, hashed_password: str) -> User:
        async with self._session_factory() as session:
            user = await session.get(User, user_id)
            if user is None:
                raise LookupError("User disappeared during password update")
            user.hashed_password = hashed_password
            await session.commit()
            await session.refresh(user)
            return user
