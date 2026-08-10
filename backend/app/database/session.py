"""Database session dependency."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.engine import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()