"""Database connection and session management."""
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from services.shared.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.database_echo,
    future=True,
)

# Create async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db() -> None:
    """Initialize database tables.
    
    This will create all tables defined in SQLModel metadata.
    Import all models before calling this function.
    """
    # Import all models to register them with SQLModel metadata
    from services.identity.models import APIToken, Role, Tenant, User, UserRole  # noqa: F401
    from services.project.models import Project, ProjectMember  # noqa: F401
    from services.work_item.models import (  # noqa: F401
        WorkItem,
        WorkItemApproval,
        WorkItemHistory,
        WorkItemLink,
    )
    from services.specification.models import ProjectSpecification, ProjectArchitecture  # noqa: F401

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        yield session


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
