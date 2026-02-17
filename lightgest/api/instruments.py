"""
instrument addition and removal.
"""

from fastapi import APIRouter, HTTPException, Request, status

from lightcurvedb.models.instrument import Instrument
from lightcurvedb.models.exceptions import InstrumentNotFoundException

from lightgest.database import DatabaseBackend

from .auth import requires

instrument_router = APIRouter(prefix="/instruments")


@instrument_router.put("/")
@requires("lcs:create")
async def instruments_put(
    request: Request,
    instrument: Instrument,
    backend: DatabaseBackend,
) -> str:
    return await backend.instruments.create(instrument=instrument)


@instrument_router.delete("/{name}")
@requires("lcs:delete")
async def instruments_delete(request: Request, name: str, backend: DatabaseBackend):
    try:
        await backend.instruments.delete(name=name)
    except InstrumentNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"instrument {name} not found"
        )
