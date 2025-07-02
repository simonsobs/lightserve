"""
Endpoints for lightcurves
"""

import io
from typing import Literal

from fastapi import APIRouter, HTTPException, Request, Response, status
from lightcurvedb.client.lightcurve import (
    BandNotFound,
    LightcurveBandResult,
    LightcurveResult,
    SourceNotFound,
    lightcurve_read_band,
    lightcurve_read_source,
)

from lightserve.database import AsyncSessionDependency
from lightserve.processing.renderer import (
    _transform_band_lc_to_csv,
    _transform_band_lc_to_hdf5,
    _transform_lc_to_csv,
    _transform_lc_to_hdf5,
)

from .auth import requires

lightcurves_router = APIRouter(prefix="/lightcurves")


@lightcurves_router.get("/{source_id}/{band_name}")
@requires("lcs:read")
async def lightcurves_get_band_lightcurve(
    request: Request, source_id: int, band_name: str, conn: AsyncSessionDependency
) -> LightcurveBandResult | LightcurveResult:
    """
    Return the lightcurve for a single band. For all bands, call `/source_id/all`.
    """

    try:
        if band_name == "all":
            return await lightcurve_read_source(id=source_id, conn=conn)
        else:
            return await lightcurve_read_band(
                id=source_id, band_name=band_name, conn=conn
            )
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found or has no observations in this band",
        )
    except BandNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Band {band_name} not found"
        )


@lightcurves_router.get("/{source_id}/{band_name}/download")
@requires("lcs:read")
async def lightcurve_download(
    request: Request,
    source_id: int,
    band_name: str,
    conn: AsyncSessionDependency,
    format: Literal["csv", "hdf5"] = "hdf5",
) -> Response:
    """
    Return the lightcurves in CSV or HDF5 format, depending on user choice.
    """
    try:
        if band_name == "all":
            lightcurve_data = await lightcurve_read_source(id=source_id, conn=conn)
            filename = f"lightcurve_source_{source_id}_all_bands.{format}"
        else:
            lightcurve_data = await lightcurve_read_band(
                id=source_id, band_name=band_name, conn=conn
            )
            filename = f"lightcurve_source_{source_id}_band_{band_name}.{format}"
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found or has no observations in this band",
        )
    except BandNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Band {band_name} not found"
        )

    if format == "csv":
        with io.StringIO() as buffer:
            if band_name == "all":
                _transform_lc_to_csv(lightcurve=lightcurve_data, handle=buffer)
            else:
                _transform_band_lc_to_csv(
                    lightcurve_band=lightcurve_data, handle=buffer
                )

            return Response(
                content=buffer.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                },
            )
    elif format == "hdf5":
        with io.BytesIO() as buffer:
            if band_name == "all":
                _transform_lc_to_hdf5(lightcurve=lightcurve_data, handle=buffer)
            else:
                _transform_band_lc_to_hdf5(
                    lightcurve_band=lightcurve_data, handle=buffer
                )

            return Response(
                content=buffer.getvalue(),
                media_type="application/x-hdf5",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}",
                },
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: {format}. Supported formats are 'csv' and 'hdf5'",
        )
