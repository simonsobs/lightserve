"""
API for adding sources.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from lightcurvedb.models.exceptions import SourceNotFoundException
from lightcurvedb.models.source import Source

from lightgest.database import DatabaseBackend

from .auth import requires

sources_router = APIRouter(prefix="/sources")


@sources_router.put("/")
@requires("lcs:create")
async def sources_put(
    request: Request,
    content: Source,
    backend: DatabaseBackend,
) -> UUID:
    return await backend.sources.create(source=content)


@sources_router.delete("/{id}")
@requires("lcs:delete")
async def sources_delete(request: Request, id: UUID, backend: DatabaseBackend):
    try:
        await backend.sources.delete(id=id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Source {id} not found"
        )
