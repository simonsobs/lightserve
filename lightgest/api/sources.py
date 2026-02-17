"""
API for adding sources.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Request, status
from lightcurvedb.models.exceptions import SourceNotFoundException
from lightcurvedb.models.source import Source

from lightgest.database import DatabaseBackend

from .auth import requires

sources_router = APIRouter(prefix="/sources", tags=["Sources"])


@sources_router.put(
    "/",
    summary="Create source",
    description="Create a new source entry. Requires scope lcs:create.",
)
@requires("lcs:create")
async def sources_put(
    request: Request,
    content: Source,
    backend: DatabaseBackend,
) -> UUID:
    return await backend.sources.create(source=content)


@sources_router.delete(
    "/{source_id}",
    summary="Delete source",
    description="Delete a source by identifier. Requires scope lcs:delete.",
)
@requires("lcs:delete")
async def sources_delete(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., description="Source identifier."),
):
    try:
        await backend.sources.delete(source_id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found",
        )
