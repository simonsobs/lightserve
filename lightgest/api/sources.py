"""
API for adding sources.
"""

from fastapi import APIRouter, HTTPException, Request, status
from lightcurvedb.client.source import SourceNotFound, source_add, source_delete
from lightcurvedb.models.source import Source

from lightgest.database import AsyncSessionDependency

from .auth import requires

sources_router = APIRouter(prefix="/sources")


@sources_router.put("/")
@requires("lcs:create")
async def sources_put(
    request: Request,
    content: Source,
    conn: AsyncSessionDependency,
) -> int:
    return await source_add(content, conn=conn)


@sources_router.delete("/{id}")
@requires("lcs:delete")
async def sources_delete(request: Request, id: int, conn: AsyncSessionDependency):
    try:
        await source_delete(id=id, conn=conn)
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Source {id} not found"
        )
