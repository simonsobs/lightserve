"""
Endpoints for lightcurves
"""

from datetime import datetime
from typing import Literal
from uuid import UUID
import io

from fastapi import APIRouter, HTTPException, Path, Query, Request, status, Response
from lightcurvedb.models.exceptions import SourceNotFoundException
from lightcurvedb.models.lightcurves import (
    SourceLightcurveBinnedFrequency,
    SourceLightcurveBinnedInstrument,
    SourceLightcurveFrequency,
    SourceLightcurveInstrument,
)

from lightserve.database import DatabaseBackend
from lightserve.processing.renderer import (
    _transform_flux_measurements_to_parquet,
    _transform_flux_measurements_to_csv,
    _transform_flux_measurements_to_hdf5,
)

from .auth import requires

lightcurves_router = APIRouter(prefix="/lightcurves", tags=["Lightcurves"])


@lightcurves_router.get(
    "/{source_id}/unbinned",
    summary="Get unbinned lightcurve",
    description=(
        "Return an unbinned lightcurve for a source, using either frequency- or "
        "instrument-selected views. Requires scope lcs:read."
    ),
)
@requires("lcs:read")
async def lightcurves_get_unbinned_lightcurve(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., description="Source identifier."),
    selection_strategy: Literal["frequency", "instrument"] = Query(
        "instrument",
        description="Choose frequency- or instrument-selected lightcurve view.",
    ),
) -> SourceLightcurveFrequency | SourceLightcurveInstrument:
    """Return the lightcurve for a single band selection."""

    try:
        return await backend.lightcurves.get_source_lightcurve(
            source_id=source_id, selection_strategy=selection_strategy
        )
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found or has no observations in this band",
        )


@lightcurves_router.get(
    "/{source_id}/binned",
    summary="Get binned lightcurve",
    description=(
        "Return a binned lightcurve for a source using a time binning strategy. "
        "Requires scope lcs:read."
    ),
)
@requires("lcs:read")
async def lightcurves_get_binned_lightcurve(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., description="Source identifier."),
    start_time: datetime = Query(
        ..., description="ISO-8601 start time for the binning window."
    ),
    end_time: datetime = Query(
        ..., description="ISO-8601 end time for the binning window."
    ),
    selection_strategy: Literal["frequency", "instrument"] = Query(
        "frequency",
        description="Choose frequency- or instrument-selected lightcurve view.",
    ),
    binning_strategy: Literal["1 day", "7 days", "30 days"] = Query(
        "7 days",
        description="Bin size for the lightcurve time series.",
    ),
) -> SourceLightcurveBinnedFrequency | SourceLightcurveBinnedInstrument:
    """Return a binned lightcurve for a single band selection."""

    try:
        return await backend.lightcurves.get_binned_source_lightcurve(
            source_id=source_id,
            selection_strategy=selection_strategy,
            binning_strategy=binning_strategy,
            start_time=start_time,
            end_time=end_time,
        )
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found or has no observations in this band",
        )


@lightcurves_router.get("/{source_id}.{file_type}")
@requires("lcs:read")
async def lightcurve_download(
    request: Request,
    backend: DatabaseBackend,
    source_id: UUID = Path(..., description="Source identifier."),
    file_type: Literal["csv", "hdf5", "parquet"] = Path(
        ..., description="File type for the lightcurve download."
    ),
) -> bytes:
    """
    Returns a lightcurve for download in one of three formats: CSV, HDF5, or Parquet.
    Requires the scope lcs:read.
    """
    try:
        all_measurements = await backend.fluxes.get_all_for_source(source_id=source_id)
    except SourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found or has no observations in this band",
        )

    # Now render the lightcurve into the requested format.
    if file_type == "csv":
        content_type = "text/csv"
        BUFFER_TYPE = io.StringIO
        WRITER = _transform_flux_measurements_to_csv
    elif file_type == "hdf5":
        content_type = "application/x-hdf5"
        BUFFER_TYPE = io.BytesIO
        WRITER = _transform_flux_measurements_to_hdf5
    elif file_type == "parquet":
        content_type = "application/x-parquet"
        BUFFER_TYPE = io.BytesIO
        WRITER = _transform_flux_measurements_to_parquet
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_type}. Supported types are 'csv', 'hdf5', and 'parquet'.",
        )

    with BUFFER_TYPE() as buffer:
        WRITER(all_measurements, buffer)

        return Response(
            content=buffer.getvalue(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=lc_{source_id}.{file_type}",
            },
        )
