"""
API for getting source information.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, Request, status
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

sources_router = APIRouter(prefix="/sources", tags=["Sources"])


@sources_router.get(
    "/cone",
    summary="Search sources in a cone",
    description=(
        "Return sources within a cone search radius in degrees. "
        "Requires scope lcs:read."
    ),
)
@requires("lcs:read")
async def sources_get_in_cone(
    request: Request,
    backend: DatabaseBackend,
    ra: float = Query(..., description="Right ascension in degrees (-180 to 180)."),
    dec: float = Query(..., description="Declination in degrees (-90 to 90)."),
    radius: float = Query(..., description="Cone radius in degrees (>= 0)."),
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


@sources_router.get(
    "/",
    summary="List sources",
    description="Return all sources with basic sky position metadata. Requires scope lcs:read.",
)
@requires("lcs:read")
async def sources_get_list(request: Request, backend: DatabaseBackend) -> list[Source]:
    """
    Get the list of all sources held by the system, along with basic information
    (e.g. their position on sky).
    """

    return await backend.sources.get_all()


@sources_router.get(
    "/feed",
    summary="Get source feed",
    description=(
        "Return a paginated feed of sources (16 per page). Requires scope lcs:read."
    ),
)
@requires("lcs:read")
async def sources_get_feed(
    request: Request,
    backend: DatabaseBackend,
    start: int = Query(0, ge=0, description="Pagination offset (zero-based)."),
) -> FeedResult:
    """
    Get the 'feed' of sourcs, starting (for pagination purposes) at zero by
    default and at higher values if requested. We read 16 sources at once.
    """

    result = await feed_read(
        start=start, number=16, band_name=settings.feed_band_name, backend=backend
    )

    return result


@sources_router.get(
    "/{source_id}",
    summary="Get source by id",
    description="Return a single source by identifier. Requires scope lcs:read.",
)
@requires("lcs:read")
async def sources_get_by_id(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., alias="id", description="Source identifier."),
) -> Source:
    """
    Get a source corresponding to a specific ID.
    """

    try:
        return await backend.sources.get_by_id(id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No source with ID {source_id}",
        )


@sources_router.get(
    "/{source_id}/summary",
    summary="Get source summary",
    description=(
        "Return summary statistics for a source, including bands and lightcurve metadata. "
        "Requires scope lcs:read."
    ),
)
@requires("lcs:read")
async def sources_get_summary(
    request: Request,
    database: DatabaseBackend,
    source_id: UUID = Path(..., alias="id", description="Source identifier."),
) -> SourceStatistics:
    """
    Get a summary of the data that we hold about a source, including its
    bands and what lightcurve information we have.
    """

    try:
        return await database.analysis.get_source_statistics(source_id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No source with ID {source_id}",
        )
