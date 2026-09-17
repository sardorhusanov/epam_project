from abc import ABC, abstractmethod
from uuid import UUID

from app.projects.models import Project


class IProjectRepository(ABC):
    @abstractmethod
    async def get_by_id(self, project_id: UUID) -> Project | None:
        raise NotImplementedError
