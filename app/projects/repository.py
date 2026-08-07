from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.projects.interfaces.repository import IProjectRepository
from app.projects.models import Project


class ProjectRepository(IProjectRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_id(self, project_id: UUID) -> Project | None:
        async with self._session_factory() as session:
            return await session.get(Project, project_id)