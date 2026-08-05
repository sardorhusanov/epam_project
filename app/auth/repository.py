from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.repository import UserRepository


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.users.get_by_email(email)

    async def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        return await self.users.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,
        )

    async def update_password(
        self,
        user: User,
        hashed_password: str,
    ) -> User:
        return await self.users.update_password(
            user=user,
            hashed_password=hashed_password,
        )