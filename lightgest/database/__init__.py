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
from lightcurvedb.storage.prototype.backend import Backend

from cachetools import cached

@cached
async def get_backend() -> Backend:
    return lightcurvedb_settings.backend


DatabaseBackend = Annotated[Backend, Depends(get_backend)]
