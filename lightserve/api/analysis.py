"""
Endpoints for lightcurve statistics analysis.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status, Query
from pydantic import BaseModel

from lightserve.database import AsyncSessionDependency
from lightcurvedb.models.analysis import BandStatistics, BandTimeSeries
from lightcurvedb.client.source import SourceNotFound, source_read
from lightcurvedb.client.band import BandNotFound, band_read
from lightcurvedb.analysis.statistics import get_band_statistics, get_band_statistics_wo_ca, get_band_timeseries


from .auth import requires

analysis_router = APIRouter(prefix="/analysis")


class BandStatisticsResponse(BaseModel):
    """
    Response model for band statistics
    """
    source_id: int
    band_name: str
    statistics: BandStatistics
    start_time: datetime | None
    end_time: datetime | None
    time_resolution: str


class BandTimeSeriesResponse(BaseModel):
    """
    Response model for band timeseries
    """
    source_id: int
    band_name: str
    timeseries: BandTimeSeries



@analysis_router.get("/aggregate/{source_id}/{band_name}")
@requires("lcs:read")
async def get_source_band_statistics(
    request: Request,
    source_id: int,
    band_name: str,
    conn: AsyncSessionDependency,
    start_time: Optional[datetime] = Query(
        None, 
        description="Start time for statistics calculation (YYYY-MM-DD)"
    ),
    end_time: Optional[datetime] = Query(
        None, 
        description="End time for statistics calculation (YYYY-MM-DD)"
    ),
) -> BandStatisticsResponse:
    """
    Calculate statistical measures for a specific source and band using Continuous Aggregate Table
    """
    try:
        await source_read(id=source_id, conn=conn)
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found"
        )
    
    try:
        await band_read(band_name, conn=conn)
    except BandNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Band '{band_name}' not found"
        )
    
    # Validate time range
    if start_time and end_time and start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time"
        )

    statistics, bucket_start, bucket_end, time_resolution = await get_band_statistics(
        source_id=source_id,
        band_name=band_name,
        conn=conn,
        start_time=start_time,
        end_time=end_time
    )

    return BandStatisticsResponse(
        source_id=source_id,
        band_name=band_name,
        statistics=statistics,
        start_time=bucket_start,
        end_time=bucket_end,
        time_resolution=time_resolution
    )


@analysis_router.get("/timeseries/{source_id}/{band_name}")
@requires("lcs:read")
async def get_source_band_timeseries(
    request: Request,
    source_id: int,
    band_name: str,
    conn: AsyncSessionDependency,
    start_time: Optional[datetime] = Query(
        None,
        description="Start time for timeseries (YYYY-MM-DD)"
    ),
    end_time: Optional[datetime] = Query(
        None,
        description="End time for timeseries (YYYY-MM-DD)"
    ),
) -> BandTimeSeriesResponse:
    """
    Get timeseries of per bucket for a specific source and band
    """
    try:
        await source_read(id=source_id, conn=conn)
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found"
        )

    try:
        await band_read(band_name, conn=conn)
    except BandNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Band '{band_name}' not found"
        )

    # Validate time range
    if start_time and end_time and start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time"
        )

    timeseries = await get_band_timeseries(
        source_id=source_id,
        band_name=band_name,
        conn=conn,
        start_time=start_time,
        end_time=end_time
    )

    return BandTimeSeriesResponse(
        source_id=source_id,
        band_name=band_name,
        timeseries=timeseries
    )


@analysis_router.get("/wo_ca/aggregate/{source_id}/{band_name}")
@requires("lcs:read")
async def get_source_band_statistics_without_continuous_aggregates(
    request: Request,
    source_id: int,
    band_name: str,
    conn: AsyncSessionDependency,
    start_time: Optional[datetime] = Query(
        None, 
        description="Start time for statistics calculation (ISO format)"
    ),
    end_time: Optional[datetime] = Query(
        None, 
        description="End time for statistics calculation (ISO format)"
    ),
) -> BandStatisticsResponse:
    """
    Calculate statistical measures for a specific source and band using FluxMeasurementTable (Not for production)
    """
    try:
        await source_read(id=source_id, conn=conn)
    except SourceNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} not found"
        )
    
    try:
        await band_read(band_name, conn=conn)
    except BandNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Band '{band_name}' not found"
        )
    
    # Validate time range
    if start_time and end_time and start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be before end_time"
        )

    statistics, _, _ = await get_band_statistics_wo_ca(
        source_id=source_id,
        band_name=band_name,
        conn=conn,
        start_time=start_time,
        end_time=end_time
    )

    return BandStatisticsResponse(
        source_id=source_id,
        band_name=band_name,
        statistics=statistics,
        start_time=start_time,
        end_time=end_time,
        time_resolution="daily"
    )