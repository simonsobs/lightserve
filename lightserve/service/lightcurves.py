"""
Marshalling lightcurves from various sources.
"""

from lightcurvedb.models.flux import FluxMeasurementTable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection


async def read_lightcurve_for_source_and_band(
    source_id: int, band_name: str, conn: AsyncConnection
) -> list[FluxMeasurementTable]:
    query = select(FluxMeasurementTable)

    query = query.filter(
        FluxMeasurementTable.source_id == source_id,
        FluxMeasurementTable.band_name == band_name,
    )

    query = query.order_by(FluxMeasurementTable.time)

    result = await conn.execute(query)

    return result.all()
