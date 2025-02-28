"""
Marshalling sources from the database.
"""

from lightcurvedb.models.flux import FluxMeasurementTable
from lightcurvedb.models.source import SourceTable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection


class SourceNotFound(Exception):
    pass


async def read_source(id: int, conn: AsyncConnection) -> SourceTable:
    res = await conn.get(SourceTable, id)

    if res is None:
        raise SourceNotFound

    return res


async def read_bands_for_source(id: int, conn: AsyncConnection) -> list[str]:
    query = select(FluxMeasurementTable.band_name)

    query = query.filter_by(
        FluxMeasurementTable.source_id == id,
    )

    query = query.distinct()

    result = await conn.execute(query)

    return result.all()
