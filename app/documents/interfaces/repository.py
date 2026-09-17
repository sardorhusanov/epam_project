from abc import ABC, abstractmethod
from uuid import UUID

from app.documents.models import Document


class IDocumentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, document_id: UUID) -> Document | None:
        raise NotImplementedError
