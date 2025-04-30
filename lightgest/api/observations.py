"""
Add observations to a source.
"""

from fastapi import APIRouter, Request
from lightcurvedb.client.cutouts import cutout_add
from lightcurvedb.client.measurement import measurement_flux_add
from lightcurvedb.models.cutout import Cutout
from lightcurvedb.models.flux import FluxMeasurement

from lightgest.database import AsyncSessionDependency

from .auth import requires

observations_router = APIRouter(prefix="/observations")


@observations_router.put("/")
@requires("lcs:create")
async def add_observation(
    request: Request,
    flux_measurement: FluxMeasurement,
    conn: AsyncSessionDependency,
    cutout: Cutout | None = None,
) -> tuple[int, int | None]:
    measurement_id = await measurement_flux_add(measurement=flux_measurement, conn=conn)

    if cutout is not None:
        enforced_cutout = Cutout(
            data=cutout.data,
            time=cutout.time,
            units=cutout.units,
            band_name=flux_measurement.band_name,
            flux_id=measurement_id,
        )

        cutout_id = await cutout_add(cutout=enforced_cutout, conn=conn)
    else:
        cutout_id = None

    return measurement_id, cutout_id
