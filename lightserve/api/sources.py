"""
API for getting source information.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from lightcurvedb.client.feed import feed_read
from lightcurvedb.client.source import (
    source_read_in_radius,
)
from lightcurvedb.models.exceptions import SourceNotFoundException
from lightcurvedb.models.feed import FeedResult
from lightcurvedb.models.source import Source
from lightcurvedb.models.statistics import SourceStatistics

from lightserve.database import DatabaseBackend

from .auth import requires
from .settings import settings

sources_router = APIRouter(prefix="/sources")


@sources_router.get("/cone")
@requires("lcs:read")
async def sources_get_in_cone(
    request: Request, ra: float, dec: float, radius: float, backend: DatabaseBackend
) -> list[Source]:
    """
    Get the sources that are within a square cone around a specific right
    ascention and declination. All values are in degrees, with
    -180 < ra < 180, -90 < dec < 90, radius >= 0.
    """

    try:
        return await source_read_in_radius(
            center=(ra, dec), radius=radius, backend=backend
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parameters for cone search",
        )


@sources_router.get("/")
@requires("lcs:read")
async def sources_get_list(request: Request, backend: DatabaseBackend) -> list[Source]:
    """
    Get the list of all sources held by the system, along with basic information
    (e.g. their position on sky).
    """

    return await backend.sources.get_all()


@sources_router.get("/feed")
@requires("lcs:read")
async def sources_get_feed(
    request: Request,
    backend: DatabaseBackend,
    start: int = 0,
) -> FeedResult:
    """
    Get the 'feed' of sourcs, starting (for pagination purposes) at zero by
    default and at higher values if requested. We read 16 sources at once.
    """

    result = await feed_read(
        start=start, number=16, band_name=settings.feed_band_name, backend=backend
    )

    return result


@sources_router.get("/{id}")
@requires("lcs:read")
async def sources_get_by_id(
    request: Request, source_id: UUID, backend: DatabaseBackend
) -> Source:
    """
    Get a source corresponding to a specific ID.
    """

    try:
        return await backend.sources.get_by_id(id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No source with ID {id}"
        )


@sources_router.get("/{id}/summary")
@requires("lcs:read")
async def sources_get_summary(
    request: Request, source_id: UUID, database: DatabaseBackend
) -> SourceStatistics:
    """
    Get a summary of the data that we hold about a source, including its
    bands and what lightcurve information we have.
    """

    try:
        return await database.analysis.get_source_statistics(source_id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No source with ID {id}"
        )
