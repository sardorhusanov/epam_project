from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.documents.interfaces.repository import IDocumentRepository
from app.documents.models import Document


class DocumentRepository(IDocumentRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def get_by_id(self, document_id: UUID) -> Document | None:
        async with self._session_factory() as session:
            return await session.get(Document, document_id)
