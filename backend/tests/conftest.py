"""
QuishGuard — Test Configuration
"""

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import init_db, Base


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize the test database."""
    await init_db()
    yield


@pytest.fixture
async def async_client():
    """Create an async HTTP client for testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
