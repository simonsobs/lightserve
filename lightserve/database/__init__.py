"""
Database is configured using the official lightcurvedb configuration
options. From there, you can use the service layers exposed through
the client. All we provide here is a sychronous and asynchronous
dependency to gain access to the database inside the FastAPI endpoints.

By importing this, you will set up two postgres connections - synchronous
and asynchronous.
"""

from typing import Annotated, Optional

from fastapi import Depends, FastAPI
from lightcurvedb.config import settings as lightcurvedb_settings
from lightcurvedb.storage.prototype.backend import Backend

# Global backend instance
_backend_instance: Optional[Backend] = None


async def get_backend() -> Backend:
    if _backend_instance is None:
        raise RuntimeError("Backend instance is not initialized.")
    yield _backend_instance


async def lifespan(app: FastAPI):
    global _backend_instance

    async with lightcurvedb_settings.backend as backend:
        app.database_backend = backend
        _backend_instance = app.database_backend
        print("Initialized global backend instance")

        yield


DatabaseBackend = Annotated[Backend, Depends(get_backend, use_cache=True)]
