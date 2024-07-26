import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.database import Database, Base
import re  # Add this import

DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Using in-memory SQLite for testing purposes

@pytest.fixture(scope="module")
async def initialize_database():
    Database.initialize(DATABASE_URL)
    async with Database._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with Database._engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(initialize_database):
    async_session_factory = Database.get_session_factory()
    async with async_session_factory() as session:
        yield session

def test_database_initialization():
    Database.initialize(DATABASE_URL)  # Initialize the database here to test initialization
    assert Database._engine is not None, "Database engine should be initialized"
    assert Database._session_factory is not None, "Session factory should be initialized"

def test_get_session_factory_uninitialized():
    """
    Test if getting a session factory without initialization raises an exception.
    """
    # Temporarily remove the initialized engine and session factory
    original_engine = Database._engine
    original_session_factory = Database._session_factory
    Database._engine = None
    Database._session_factory = None

    try:
        with pytest.raises(ValueError, match=re.escape("Database not initialized. Call `initialize()` first.")):
            Database.get_session_factory()
    finally:
        # Restore the original engine and session factory
        Database._engine = original_engine
        Database._session_factory = original_session_factory

@pytest.mark.asyncio
async def test_database_session(db_session: AsyncSession):
    assert isinstance(db_session, AsyncSession), "Session should be an instance of AsyncSession"
