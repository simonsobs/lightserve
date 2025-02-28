"""
Database is configured using the official lightcurvedb configuration
options. From there, you can use the service layers exposed through
the client. All we provide here is a sychronous and asynchronous
dependency to gain access to the database inside the FastAPI endpoints.

By importing this, you will set up two postgres connections - synchronous
and asynchronous.
"""

from typing import Annotated

from fastapi import Depends
from lightcurvedb.config import settings as lightcurvedb_settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

ASYNC_MANAGER = lightcurvedb_settings.async_manager()
SYNC_MANAGER = lightcurvedb_settings.sync_manager()


async def get_async_session():
    async with ASYNC_MANAGER.session() as session:
        yield session


def get_sync_session():
    with SYNC_MANAGER.session() as session:
        yield session


AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
SyncSessionDependency = Annotated[Session, Depends(get_sync_session)]
