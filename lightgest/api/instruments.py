"""
instrument addition and removal.
"""

from fastapi import APIRouter, HTTPException, Path, Request, status
from lightcurvedb.models.exceptions import InstrumentNotFoundException
from lightcurvedb.models.instrument import Instrument

from lightgest.database import DatabaseBackend

from .auth import requires

instrument_router = APIRouter(prefix="/instruments", tags=["Instruments"])


@instrument_router.put(
    "/",
    summary="Create instrument",
    description="Create a new instrument entry. Requires scope lcs:create.",
)
@requires("lcs:create")
async def instruments_put(
    request: Request,
    instrument: Instrument,
    backend: DatabaseBackend,
) -> str:
    return await backend.instruments.create(instrument=instrument)


@instrument_router.delete(
    "/{module}/{frequency}",
    summary="Delete instrument",
    description="Delete an instrument by name. Requires scope lcs:delete.",
)
@requires("lcs:delete")
async def instruments_delete(
    request: Request,
    backend: DatabaseBackend,
    module: str = Path(..., description="Instrument module."),
    frequency: int = Path(..., description="Instrument frequency."),
):
    try:
        await backend.instruments.delete(frequency=frequency, module=module)
    except InstrumentNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Insturment {module} at {frequency} GHz not found",
        )
