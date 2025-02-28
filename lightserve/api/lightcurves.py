"""
Endpoints for lightcurves
"""

from fastapi import APIRouter, HTTPException, status
from lightcurvedb.client.lightcurve import (
    BandNotFound,
    LightcurveBandResult,
    LightcurveResult,
    SourceNotFound,
    lightcurve_read_band,
    lightcurve_read_source,
)

from lightserve.database import AsyncSessionDependency

lightcurves_router = APIRouter(prefix="/lightcurves")


@lightcurves_router.get("/{source_id}/{band_name}")
async def lightcurves_get_band_lightcurve(
    source_id: int, band_name: str, conn: AsyncSessionDependency
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
