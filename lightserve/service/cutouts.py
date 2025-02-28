"""
Marshalling cutouts from the database.
"""

from lightcurvedb.models.cutout import CutoutTable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection


async def get_cutout_from_flux_id(id: int, conn: AsyncConnection) -> CutoutTable:
    query = select(CutoutTable).filter_by(flux_id=id).limit(1)
    result = await conn.execute(query)
    return result.one_or_none()
