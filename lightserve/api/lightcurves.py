"""
Endpoints for lightcurves
"""

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
from lightserve.processing.renderer import _transform_lc_to_csv, _transform_lc_to_hdf5

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
):
    """
    Return the lightcurves in CSV or HDF5 format, depending on user choice
    """

    # Read the file in the similar manner as above file
    try:
        if band_name == "all":
            lightcurve_file = await lightcurve_read_band(
                id=source_id, band_name=band_name, conn=conn
            )
            filename = f"lightcurve_source_{source_id}_all_bands.{format}"
        else:
            lightcurve_file = await lightcurve_read_source(id=source_id, conn=conn)
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
        file_content, media_type = _transform_lc_to_csv(lightcurve_file)
    elif format == "hdf5":
        file_content, media_type = _transform_lc_to_hdf5(lightcurve_file)

    return Response(
        content=file_content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        },
    )
