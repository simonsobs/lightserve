"""
API for getting source information.
"""

from fastapi import APIRouter, HTTPException, status
from lightcurvedb.client.source import (
    SourceNotFound,
    SourceSummaryResult,
    source_read,
    source_read_all,
    source_read_bands,
    source_read_summary,
)
from lightcurvedb.models.source import Source

from lightserve.database import AsyncSessionDependency

sources_router = APIRouter(prefix="/sources")


@sources_router.get("/")
async def sources_get_list(conn: AsyncSessionDependency) -> list[Source]:
    """
    Get the list of all sources held by the system, along with basic information
    (e.g. their position on sky).
    """

    return await source_read_all(conn=conn)


@sources_router.get("/{id}")
async def sources_get_by_id(id: int, conn: AsyncSessionDependency) -> Source:
    """
    Get a source corresponding to a specific ID.
    """

    try:
        return await source_read(id=id, conn=conn)
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No source with ID {id}"
        )


@sources_router.get("/{id}/bands")
async def sources_get_bands_for_source(
    id: int, conn: AsyncSessionDependency
) -> list[str]:
    """
    Get (just) the list of bands for a source. However, you probably want
    `/{id}/summary`.
    """

    return await source_read_bands(id=id, conn=conn)


@sources_router.get("/{id}/summary")
async def sources_get_summary(
    id: int, conn: AsyncSessionDependency
) -> SourceSummaryResult:
    """
    Get a summary of the data that we hold about a source, including its
    bands and what lightcurve information we have.
    """

    try:
        return await source_read_summary(id=id, conn=conn)
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No source with ID {id}"
        )
