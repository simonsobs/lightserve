"""
API for getting unassigned source information.
"""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, Query, Request, status
from typing import Literal

from lightcurvedb.models.exceptions import SourceNotFoundException
from lightcurvedb.models.unassigned_source import UnassignedSource
from lightcurvedb.models.unassigned_flux import UnassignedFluxMeasurement
from lightserve.database import DatabaseBackend

from .auth import requires
from .settings import settings

unassigned_sources_router = APIRouter(prefix="/unassigned", tags=["Unassigned sources"])


@unassigned_sources_router.get(
    "/",
    summary="List unassigned sources",
    description="Return all unassigned sources with basic sky position metadata. Requires scope lcs:read.",
)
@requires("lcs:read")
async def unassigned_sources_get_list(request: Request, backend: DatabaseBackend) -> list[UnassignedSource]:
    """
    Get the list of all sources held by the system, along with basic information
    (e.g. their position on sky).
    """

    return await backend.unassigned_sources.get_all()


@unassigned_sources_router.get(
    "/search",
    summary="Get unassigned sources within an ICRS great-circle cone search",
    description="Return a list of unassigned sources within an ICRS cone search. Requires scope lcs:read."
)
@requires("lcs:read")
async def unassigned_sources_get_in_radius(
    request: Request,
    backend: DatabaseBackend,
    ra: float,
    dec: float,
    radius_arcmin: float = 2,
    status: Literal["unmatched", "merged", "external_match", "novel", "noise"]
    | None = None,
) -> list[UnassignedSource]:
    """
    Get unassigned sources within a cone search.
    """

    try:
        return await backend.unassigned_sources.get_in_radius(ra=ra, dec=dec, radius_arcmin=radius_arcmin, status=status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid parameters for cone search"
        )


@unassigned_sources_router.get(
    "/{source_id}",
    summary="Get unassigned source by id",
    description="Return a single unassigned source by identifier. Requires scope lcs:read."
)
@requires("lcs:read")
async def unassigned_sources_get_by_id(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., description="Unassigned source identifier.")
) -> UnassignedSource:
    """
    Get an unassigned source corresponding to a specific ID.
    """

    try:
        return await backend.unassigned_sources.get(source_id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No unassigned source with ID {source_id}"
        )


@unassigned_sources_router.get(
    "/flux/{source_id}",
    summary="Get flux measurements for an unassigned source by id",
    description="Return flux measurements for an unassigned source by identifier. Requires scope lcs:read."
)
@requires("lcs:read")
async def unassigned_flux_get_for_source(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., description="Unassigned source identifier.")
) -> list[UnassignedFluxMeasurement]:
    """
    Get flux for an unassigned source corresponding to a specific ID.
    """

    try:
        return await backend.unassigned_fluxes.get_for_source(source_id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No flux data for unassigned source with ID {source_id}"
        )