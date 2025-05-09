"""
Band addition and removal.
"""

from fastapi import APIRouter, HTTPException, Request, status
from lightcurvedb.client.band import BandNotFound, band_add, band_delete
from lightcurvedb.models.band import Band

from lightgest.database import AsyncSessionDependency

from .auth import requires

band_router = APIRouter(prefix="/bands")


@band_router.put("/")
@requires("lcs:create")
async def bands_put(
    request: Request,
    band: Band,
    conn: AsyncSessionDependency,
) -> str:
    return await band_add(band=band, conn=conn)


@band_router.delete("/{name}")
@requires("lcs:delete")
async def bands_delete(request: Request, name: str, conn: AsyncSessionDependency):
    try:
        await band_delete(name=name, conn=conn)
    except BandNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Band {name} not found"
        )
