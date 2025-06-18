"""
Endpoints for lightcurves
"""
import io
import csv
from typing import Literal
import h5py
from fastapi import APIRouter, HTTPException, Request, status, Response
from lightcurvedb.client.lightcurve import (
    BandNotFound,
    BAND_RESULT_ITEMS,
    LightcurveBandResult,
    LightcurveResult,
    SourceNotFound,
    lightcurve_read_band,
    lightcurve_read_source,
)

from lightserve.database import AsyncSessionDependency

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
    request: Request, source_id: int, band_name: str, conn: AsyncSessionDependency, format: Literal["csv","hdf5"]="hdf5"):
    """
    Return the lightcurves in CSV or HDF5 format, depending on user choice
    """

    # Read the file in the similar manner as above file
    try:
        if band_name == "all":
            lightcurve_file = await lightcurve_read_band(id=source_id, band_name=band_name, conn=conn)
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
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Band {band_name} not found")


    if format == "csv":
        file_content, media_type = _transform_to_csv(lightcurve_file)
    elif format == "hdf5":
        file_content, media_type = _transform_to_hdf5(lightcurve_file)

    return Response(content=file_content,media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
        }
    )


def _transform_to_csv(lightcurve_file: LightcurveBandResult | LightcurveResult) -> tuple[bytes, str]:
    output = io.StringIO()
    csv_writer = csv.writer(output)
    if isinstance(lightcurve_file, LightcurveBandResult):
        csv_writer.writerow("measurement_id","time", "flux", "flux_uncertainty", "ra", "dec", 
            "ra_uncertainty", "dec_uncertainty", "band_name")
        for i in range(len(lightcurve_file.time)):
            csv_writer.writerow([lightcurve_file.id[i],lightcurve_file.time[i], lightcurve_file.i_flux[i], lightcurve_file.i_uncertainty[i], lightcurve_file.ra[i], lightcurve_file.dec[i], lightcurve_file.ra_uncertainty[i], lightcurve_file.dec_uncertainty[i],lightcurve_file.band.name])
    if isinstance(lightcurve_file, LightcurveResult):
        csv_writer.writerow(["measurement_id","time", "flux", "flux_uncertainty", "ra", "dec", 
            "ra_uncertainty", "dec_uncertainty", "band_name"])
        for band_data in lightcurve_file.bands:
            for i in range(len(band_data.time)):
                csv_writer.writerow([band_data.id[i],band_data.time[i], band_data.i_flux[i], band_data.i_uncertainty[i], band_data.ra[i], band_data.dec[i], band_data.ra_uncertainty[i], band_data.dec_uncertainty[i],band_data.band.name])
    csv_content = output.getvalue()
    media_type = "text/csv"
    return csv_content, media_type

def _transform_to_hdf5(lightcurve_file: LightcurveBandResult | LightcurveResult) -> tuple[bytes, str]:
    output = io.BytesIO()
    with h5py.File(output, 'w') as hf:
        if isinstance(lightcurve_file, LightcurveBandResult):
            hf.create_dataset("measurement_id", data=lightcurve_file.id)
            hf.create_dataset("time", data=[t.isoformat() for t in lightcurve_file.time])
            hf.create_dataset("flux", data=lightcurve_file.i_flux)
            hf.create_dataset("flux_uncertainty", data=lightcurve_file.i_uncertainty)
            hf.create_dataset("ra", data=lightcurve_file.ra)
            hf.create_dataset("dec", data=lightcurve_file.dec)
            hf.create_dataset("ra_uncertainty", data=lightcurve_file.ra_uncertainty)
            hf.create_dataset("dec_uncertainty", data=lightcurve_file.dec_uncertainty)
            hf.create_dataset("band_name", data=lightcurve_file.band.name)
        elif isinstance(lightcurve_file, LightcurveResult):
            for band_data in lightcurve_file.bands:
                band_group = hf.create_group(band_data.band.name)
                band_group.create_dataset("measurement_id", data=band_data.id)
                band_group.create_dataset("time", data=[t.isoformat() for t in band_data.time])
                band_group.create_dataset("flux", data=band_data.i_flux)
                band_group.create_dataset("flux_uncertainty", data=band_data.i_uncertainty)
                band_group.create_dataset("ra", data=band_data.ra)
                band_group.create_dataset("dec", data=band_data.dec)
                band_group.create_dataset("ra_uncertainty", data=band_data.ra_uncertainty)
                band_group.create_dataset("dec_uncertainty", data=band_data.dec_uncertainty)
                band_group.create_dataset("band_name", data=band_data.band.name)
    hdf5_content = output.getvalue()
    media_type = "application/x-hdf5"
    return hdf5_content, media_type
    


            